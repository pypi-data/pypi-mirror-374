"""
Consolidated AWS Operations Utility

This module provides integrated AWS operation patterns to eliminate duplication across handlers.
Consolidates: instance management, operation execution, describe operations, logging, and status checking.
"""

from typing import Any, Callable, Optional

from botocore.exceptions import ClientError

from domain.base.dependency_injection import injectable
from domain.base.ports import ConfigurationPort, LoggingPort
from domain.request.aggregate import Request
from infrastructure.resilience import CircuitBreakerOpenError
from providers.aws.domain.template.aggregate import AWSTemplate
from providers.aws.exceptions.aws_exceptions import AWSInfrastructureError
from providers.aws.infrastructure.aws_client import AWSClient
from providers.aws.utilities.fleet_tag_builder import FleetTagBuilder


@injectable
class AWSOperations:
    """Integrated AWS operations utility with all common patterns."""

    def __init__(
        self,
        aws_client: AWSClient,
        logger: LoggingPort,
        config_port: Optional[ConfigurationPort] = None,
    ) -> None:
        """
        Initialize AWS operations utility.

        Args:
            aws_client: AWS client instance
            logger: Logger for logging messages
            config_port: Configuration port for package info
        """
        self.aws_client = aws_client
        self._logger = logger
        self._config_port = config_port
        self._retry_with_backoff = None  # Will be set by the handler

    def set_retry_method(self, retry_method: Callable) -> None:
        """
        Set the handler's retry method.

        Args:
            retry_method: Handler's retry method (_retry_with_backoff)
        """
        self._retry_with_backoff = retry_method

    def terminate_instances_with_fallback(
        self,
        instance_ids: list[str],
        request_adapter: Optional[Any] = None,
        operation_context: str = "instances",
    ) -> dict[str, Any]:
        """
        Integrated instance termination with adapter fallback.

        Eliminates 60+ lines of duplication across 4 handlers.

        Args:
            instance_ids: List of instance IDs to terminate
            request_adapter: Optional request adapter for termination
            operation_context: Context for logging (e.g., "fleet instances", "ASG instances")

        Returns:
            Termination result
        """
        if not instance_ids:
            self._logger.warning("No instance IDs provided for %s termination", operation_context)
            return {"terminated_instances": []}

        self._logger.info(
            "Terminating %s %s: %s", len(instance_ids), operation_context, instance_ids
        )

        try:
            if request_adapter:
                self._logger.info("Using request adapter for %s termination", operation_context)
                result = request_adapter.terminate_instances(instance_ids)
                self._logger.info("Request adapter termination result: %s", result)
                return result
            else:
                self._logger.info("Using EC2 client directly for %s termination", operation_context)
                if not self._retry_with_backoff:
                    raise ValueError("Retry method not set. Call set_retry_method first.")

                result = self._retry_with_backoff(
                    self.aws_client.ec2_client.terminate_instances,
                    operation_type="critical",
                    InstanceIds=instance_ids,
                )
                self._logger.info("Successfully terminated %s: %s", operation_context, instance_ids)
                return result

        except Exception as e:
            self._logger.error("Failed to terminate %s: %s", operation_context, str(e))
            raise

    def execute_operation_with_standard_handling(
        self,
        operation: Callable,
        operation_name: str,
        operation_type: str = "standard",
        success_message: Optional[str] = None,
        error_message: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Execute AWS operation with integrated retry, logging, and exception handling.

        Eliminates 72+ lines of exception handling duplication.

        Args:
            operation: AWS operation to execute
            operation_name: Human-readable operation name for logging
            operation_type: Retry strategy type (critical/read_only/standard)
            success_message: Custom success message template
            error_message: Custom error message template
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            CircuitBreakerOpenError: When circuit breaker is open
            AWSInfrastructureError: For AWS operation failures
        """
        try:
            self._logger.debug(
                "Executing %s with operation_type=%s", operation_name, operation_type
            )

            if not self._retry_with_backoff:
                raise ValueError("Retry method not set. Call set_retry_method first.")

            result = self._retry_with_backoff(operation, operation_type=operation_type, **kwargs)

            if success_message:
                self._logger.info(success_message)
            else:
                self._logger.info("Successfully completed %s", operation_name)

            return result

        except CircuitBreakerOpenError as e:
            error_msg = f"Circuit breaker OPEN for {operation_name}: {e!s}"
            self._logger.error(error_msg)
            raise

        except ClientError:
            # Let the handler's _convert_client_error handle this
            raise

        except Exception as e:
            error_msg = error_message or f"Unexpected error in {operation_name}: {e!s}"
            self._logger.error(error_msg)
            raise AWSInfrastructureError(error_msg)

    def describe_with_pagination_and_retry(
        self, client_method: Callable, result_key: str, operation_name: str, **filters
    ) -> list[dict[str, Any]]:
        """
        Integrated describe operations with pagination and retry.

        Eliminates 8 similar pagination patterns.

        Args:
            client_method: AWS client method to call
            result_key: Key in response containing the results
            operation_name: Operation name for logging
            **filters: AWS API filters/parameters

        Returns:
            List of resources
        """
        self._logger.debug("Describing %s with filters: %s", operation_name, filters)

        try:
            if not self._retry_with_backoff:
                raise ValueError("Retry method not set. Call set_retry_method first.")

            # Use the handler's existing _paginate method through retry
            result = self._retry_with_backoff(
                lambda: self._paginate_method(client_method, result_key, **filters),
                operation_type="read_only",
            )

            self._logger.debug("Found %s %s", len(result), operation_name)
            return result

        except Exception as e:
            self._logger.error("Failed to describe %s: %s", operation_name, str(e))
            raise

    def _paginate_method(
        self, client_method: Callable, result_key: str, **kwargs
    ) -> list[dict[str, Any]]:
        """Access handler's pagination functionality."""
        # This will be set by the handler when initializing AWSOperations
        if hasattr(self, "_paginate_func"):
            return self._paginate_func(client_method, result_key, **kwargs)
        else:
            # Fallback to simple call without pagination
            response = client_method(**kwargs)
            return response.get(result_key, [])

    def set_pagination_method(self, paginate_func: Callable) -> None:
        """Set the handler's pagination method."""
        self._paginate_func = paginate_func

    def log_operation_start(
        self,
        operation: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        **context,
    ) -> None:
        """Standardized operation start logging."""
        if resource_id:
            self._logger.info("Starting %s for %s: %s", operation, resource_type, resource_id)
        else:
            self._logger.info("Starting %s for %s", operation, resource_type)

        if context:
            self._logger.debug("%s context: %s", operation, context)

    def log_operation_success(
        self, operation: str, resource_type: str, resource_id: str, **context
    ) -> None:
        """Standardized operation success logging."""
        self._logger.info(
            "Successfully completed %s for %s: %s",
            operation,
            resource_type,
            resource_id,
        )

        if context:
            self._logger.debug("%s success context: %s", operation, context)

    def log_operation_failure(
        self,
        operation: str,
        resource_type: str,
        error: Exception,
        resource_id: Optional[str] = None,
    ) -> None:
        """Standardized operation failure logging."""
        if resource_id:
            self._logger.error(
                "Failed %s for %s %s: %s",
                operation,
                resource_type,
                resource_id,
                str(error),
            )
        else:
            self._logger.error("Failed %s for %s: %s", operation, resource_type, str(error))

    def check_resource_status(
        self,
        resource_type: str,
        resource_id: str,
        describe_method: Callable,
        status_path: str,
        expected_status: Optional[str] = None,
        **describe_params,
    ) -> str:
        """
        Integrated resource status checking.

        Args:
            resource_type: Type of resource (e.g., "EC2 Fleet", "ASG")
            resource_id: Resource identifier
            describe_method: Method to describe the resource
            status_path: Path to status in response (e.g., "FleetState", "LifecycleState")
            expected_status: Optional expected status for validation
            **describe_params: Parameters for describe method

        Returns:
            Current resource status
        """
        try:
            self._logger.debug("Checking status for %s: %s", resource_type, resource_id)

            if not self._retry_with_backoff:
                raise ValueError("Retry method not set. Call set_retry_method first.")

            response = self._retry_with_backoff(
                describe_method, operation_type="read_only", **describe_params
            )

            # Navigate to status using dot notation path
            current_status = response
            for path_part in status_path.split("."):
                if isinstance(current_status, list) and current_status:
                    current_status = current_status[0]  # Take first item for lists
                current_status = current_status.get(path_part, "unknown")

            self._logger.debug("%s %s status: %s", resource_type, resource_id, current_status)

            if expected_status and current_status != expected_status:
                self._logger.warning(
                    "%s %s status is %s, expected %s",
                    resource_type,
                    resource_id,
                    current_status,
                    expected_status,
                )

            return str(current_status)

        except Exception as e:
            self._logger.error(
                "Failed to check %s %s status: %s", resource_type, resource_id, str(e)
            )
            return "unknown"

    def get_resource_instances(
        self,
        resource_type: str,
        resource_id: str,
        describe_instances_method: Callable,
        instances_key: str,
        **describe_params,
    ) -> list[str]:
        """
        Get instance IDs associated with a resource.

        Args:
            resource_type: Type of resource
            resource_id: Resource identifier
            describe_instances_method: Method to get instances
            instances_key: Key containing instances in response
            **describe_params: Parameters for describe method

        Returns:
            List of instance IDs
        """
        try:
            self._logger.debug("Getting instances for %s: %s", resource_type, resource_id)

            if not self._retry_with_backoff:
                raise ValueError("Retry method not set. Call set_retry_method first.")

            response = self._retry_with_backoff(
                describe_instances_method, operation_type="read_only", **describe_params
            )

            instances = response.get(instances_key, [])
            instance_ids = []

            for instance in instances:
                if isinstance(instance, dict):
                    instance_id = instance.get("InstanceId")
                    if instance_id:
                        instance_ids.append(instance_id)
                elif isinstance(instance, str):
                    instance_ids.append(instance)

            self._logger.debug(
                "Found %s instances for %s %s",
                len(instance_ids),
                resource_type,
                resource_id,
            )
            return instance_ids

        except Exception as e:
            self._logger.error(
                "Failed to get instances for %s %s: %s",
                resource_type,
                resource_id,
                str(e),
            )
            return []

    def execute_with_standard_error_handling(
        self,
        operation: Callable,
        operation_name: str,
        context: str = "AWS operation",
        **kwargs,
    ) -> Any:
        """
        Execute AWS operation with standardized error handling.

        Consolidates the try/catch pattern used in all handlers to eliminate duplication.
        Provides consistent error conversion, logging, and exception raising.

        Args:
            operation: The AWS operation to execute
            operation_name: Human-readable name for logging
            context: Context for error messages
            **kwargs: Arguments to pass to the operation

        Returns:
            Result of the operation

        Raises:
            Appropriate domain exception based on AWS error type
        """
        try:
            self.log_operation_start(operation_name, context)
            result = operation(**kwargs)
            self.log_operation_success(operation_name, context, result)
            return result
        except ClientError as e:
            error = self._convert_client_error(e, operation_name)
            self.log_operation_failure(operation_name, context, error)
            raise error
        except Exception as e:
            error_msg = f"Failed to {operation_name}: {e!s}"
            self._logger.error("Unexpected error in %s: %s", context, error_msg)
            raise AWSInfrastructureError(error_msg)

    def _convert_client_error(
        self, error: ClientError, operation_name: str = "AWS operation"
    ) -> Exception:
        """
        Convert AWS ClientError to appropriate domain exception.

        Consolidates error conversion logic that was duplicated across all handlers.

        Args:
            error: The AWS ClientError to convert
            operation_name: Name of the operation for error context

        Returns:
            Appropriate domain exception
        """
        error_code = error.response.get("Error", {}).get("Code", "Unknown")
        error_message = error.response.get("Error", {}).get("Message", str(error))

        # Import here to avoid circular imports
        from providers.aws.exceptions.aws_exceptions import (
            AWSEntityNotFoundError,
            AWSInfrastructureError,
            AWSPermissionError,
            AWSRateLimitError,
            AWSValidationError,
        )

        # Map AWS error codes to domain exceptions
        if error_code in [
            "InvalidParameterValue",
            "InvalidParameter",
            "ValidationException",
        ]:
            return AWSValidationError(f"{operation_name} failed: {error_message}")
        elif error_code in [
            "ResourceNotFound",
            "InvalidGroupId.NotFound",
            "InvalidInstanceID.NotFound",
        ]:
            return AWSEntityNotFoundError(f"{operation_name} failed: {error_message}")
        elif error_code in [
            "Throttling",
            "RequestLimitExceeded",
            "TooManyRequestsException",
        ]:
            return AWSRateLimitError(f"{operation_name} failed: {error_message}")
        elif error_code in ["UnauthorizedOperation", "AccessDenied", "Forbidden"]:
            return AWSPermissionError(f"{operation_name} failed: {error_message}")
        else:
            return AWSInfrastructureError(f"{operation_name} failed: {error_message}")

    # Tagging Operations
    def apply_base_tags_to_resource(
        self, resource_id: str, request: Request, template: AWSTemplate
    ) -> bool:
        """Apply base tags to AWS resource with retry and graceful failure.

        Args:
            resource_id: AWS resource ID or ARN
            request: Request domain entity
            template: AWS template domain entity

        Returns:
            True if tagging succeeded, False if failed (with warning logged)
        """
        try:
            package_name = self._get_package_name()
            tags = FleetTagBuilder.build_base_tags(request, template, package_name)
            aws_tags = FleetTagBuilder.format_for_aws(tags)

            self.aws_client.ec2_client.create_tags(Resources=[resource_id], Tags=aws_tags)
            self._logger.debug(f"Successfully tagged resource {resource_id} with base tags")
            return True

        except Exception as e:
            self._logger.warning(f"Failed to tag resource {resource_id}: {e}")
            return False

    def discover_and_tag_fleet_instances(
        self, fleet_id: str, request: Request, template: AWSTemplate, provider_api: str
    ) -> int:
        """Discover fleet instances and apply base tags.

        Args:
            fleet_id: Fleet ID (EC2Fleet or SpotFleet)
            request: Request domain entity
            template: AWS template domain entity
            provider_api: Provider API type (ec2_fleet or spot_fleet)

        Returns:
            Number of instances successfully tagged
        """
        try:
            # Discover instances based on fleet type
            if provider_api.lower() == "ec2_fleet":
                instance_ids = self._get_ec2_fleet_instances(fleet_id)
            elif provider_api.lower() == "spot_fleet":
                instance_ids = self._get_spot_fleet_instances(fleet_id)
            else:
                self._logger.warning(f"Unknown provider_api for fleet tagging: {provider_api}")
                return 0

            if not instance_ids:
                self._logger.info(f"No instances found for fleet {fleet_id}")
                return 0

            # Tag each instance
            tagged_count = 0
            for instance_id in instance_ids:
                if self.apply_base_tags_to_resource(instance_id, request, template):
                    tagged_count += 1

            self._logger.info(
                f"Tagged {tagged_count}/{len(instance_ids)} instances for fleet {fleet_id}"
            )
            return tagged_count

        except Exception as e:
            self._logger.error(f"Failed to discover and tag fleet instances for {fleet_id}: {e}")
            return 0

    def _get_ec2_fleet_instances(self, fleet_id: str) -> list[str]:
        """Get instance IDs from EC2 Fleet."""
        try:
            response = self.aws_client.ec2_client.describe_fleet_instances(FleetId=fleet_id)
            return [instance["InstanceId"] for instance in response.get("ActiveInstances", [])]
        except Exception as e:
            self._logger.error(f"Failed to get EC2Fleet instances for {fleet_id}: {e}")
            return []

    def _get_spot_fleet_instances(self, spot_fleet_id: str) -> list[str]:
        """Get instance IDs from Spot Fleet."""
        try:
            response = self.aws_client.ec2_client.describe_spot_fleet_instances(
                SpotFleetRequestId=spot_fleet_id
            )
            return [instance["InstanceId"] for instance in response.get("ActiveInstances", [])]
        except Exception as e:
            self._logger.error(f"Failed to get SpotFleet instances for {spot_fleet_id}: {e}")
            return []

    def _get_package_name(self) -> str:
        """Get package name for CreatedBy tag with fallback."""
        if self._config_port:
            try:
                package_info = self._config_port.get_package_info()
                return package_info.get("name", "open-hostfactory-plugin")
            except Exception:  # nosec B110 - Intentional fallback to default package name
                pass
        return "open-hostfactory-plugin"

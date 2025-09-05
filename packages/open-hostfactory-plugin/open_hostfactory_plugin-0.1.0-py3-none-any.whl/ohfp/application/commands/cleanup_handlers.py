"""Domain cleanup command handlers following CQRS pattern."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from application.base.handlers import BaseCommandHandler
from application.decorators import command_handler
from application.dto.commands import (
    CleanupAllResourcesCommand,
    CleanupOldRequestsCommand,
)
from domain.base import UnitOfWorkFactory
from domain.base.events.infrastructure_events import ResourcesCleanedEvent
from domain.base.ports import ErrorHandlingPort, EventPublisherPort, LoggingPort
from domain.machine.repository import MachineRepository
from domain.request.repository import RequestRepository


@command_handler(CleanupOldRequestsCommand)
class CleanupOldRequestsHandler(BaseCommandHandler[CleanupOldRequestsCommand, dict[str, Any]]):
    """Handler for cleaning up old requests using domain commands."""

    def __init__(
        self,
        request_repository: RequestRepository,
        uow_factory: UnitOfWorkFactory,
        logger: LoggingPort,
        event_publisher: EventPublisherPort,
        error_handler: ErrorHandlingPort,
    ) -> None:
        """Initialize the instance."""
        super().__init__(logger, event_publisher, error_handler)
        self._request_repository = request_repository
        self._uow_factory = uow_factory

    async def validate_command(self, command: CleanupOldRequestsCommand) -> None:
        """Validate cleanup old requests command."""
        await super().validate_command(command)
        if command.older_than_days <= 0:
            raise ValueError("older_than_days must be positive")

    async def execute_command(self, command: CleanupOldRequestsCommand) -> dict[str, Any]:
        """Handle cleanup old requests command."""
        self.logger.info("Cleaning up requests older than %s days", command.older_than_days)
        cutoff_date = datetime.utcnow() - timedelta(days=command.older_than_days)

        try:
            with self._uow_factory.create_unit_of_work() as uow:
                # Find old requests to cleanup
                old_requests = uow.requests.find_old_requests(
                    cutoff_date=cutoff_date, statuses=command.statuses_to_cleanup
                )

                if command.dry_run:
                    self.logger.info("DRY RUN: Would cleanup %s requests", len(old_requests))
                    return {
                        "dry_run": True,
                        "requests_found": len(old_requests),
                        "request_ids": [str(req.request_id) for req in old_requests],
                    }

                # Actually cleanup requests
                cleaned_count = 0
                for request in old_requests:
                    try:
                        uow.requests.delete(request.request_id)
                        cleaned_count += 1
                        self.logger.debug("Cleaned up request: %s", request.request_id)
                    except Exception as e:
                        # Per-item exception handling - appropriate to keep
                        self.logger.error("Failed to cleanup request %s: %s", request.request_id, e)

                uow.commit()

                # Publish cleanup event
                cleanup_event = ResourcesCleanedEvent(
                    aggregate_id="cleanup-operation",
                    aggregate_type="CleanupOperation",
                    resource_type="Request",
                    resource_id="multiple",
                    provider="system",
                    resource_count=cleaned_count,
                    cleanup_reason=f"Cleanup requests older than {command.older_than_days} days",
                )
                self.event_publisher.publish(cleanup_event)

                self.logger.info("Successfully cleaned up %s old requests", cleaned_count)
                return {
                    "success": True,
                    "requests_cleaned": cleaned_count,
                    "cutoff_date": cutoff_date.isoformat(),
                }

        except Exception as e:
            self.logger.error("Failed to cleanup old requests: %s", e)
            raise


@command_handler(CleanupAllResourcesCommand)
class CleanupAllResourcesHandler(BaseCommandHandler[CleanupAllResourcesCommand, dict[str, Any]]):
    """Handler for cleaning up all resources (requests and machines)."""

    def __init__(
        self,
        request_repository: RequestRepository,
        machine_repository: MachineRepository,
        uow_factory: UnitOfWorkFactory,
        logger: LoggingPort,
        event_publisher: EventPublisherPort,
        error_handler: ErrorHandlingPort,
    ) -> None:
        super().__init__(logger, event_publisher, error_handler)
        self._request_repository = request_repository
        self._machine_repository = machine_repository
        self._uow_factory = uow_factory

    async def validate_command(self, command: CleanupAllResourcesCommand) -> None:
        """Validate cleanup all resources command."""
        await super().validate_command(command)
        if command.older_than_days <= 0:
            raise ValueError("older_than_days must be positive")

    async def execute_command(self, command: CleanupAllResourcesCommand) -> dict[str, Any]:
        """Handle cleanup all resources command."""
        self.logger.info("Cleaning up all resources older than %s days", command.older_than_days)
        cutoff_date = datetime.utcnow() - timedelta(days=command.older_than_days)

        try:
            with self._uow_factory.create_unit_of_work() as uow:
                # Find resources to cleanup
                old_requests = uow.requests.find_old_requests(
                    cutoff_date=cutoff_date, include_pending=command.include_pending
                )

                old_machines = uow.machines.find_old_machines(
                    cutoff_date=cutoff_date,
                    statuses=(["terminated", "failed"] if not command.include_pending else None),
                )

                if command.dry_run:
                    self.logger.info(
                        "DRY RUN: Would cleanup %s requests and %s machines",
                        len(old_requests),
                        len(old_machines),
                    )
                    return {
                        "dry_run": True,
                        "requests_found": len(old_requests),
                        "machines_found": len(old_machines),
                    }

                # Cleanup resources
                requests_cleaned = 0
                machines_cleaned = 0

                # Cleanup requests
                for request in old_requests:
                    try:
                        uow.requests.delete(request.request_id)
                        requests_cleaned += 1
                    except Exception as e:
                        # Per-item exception handling - appropriate to keep
                        self.logger.error("Failed to cleanup request %s: %s", request.request_id, e)

                # Cleanup machines
                for machine in old_machines:
                    try:
                        uow.machines.delete(machine.machine_id)
                        machines_cleaned += 1
                    except Exception as e:
                        # Per-item exception handling - appropriate to keep
                        self.logger.error("Failed to cleanup machine %s: %s", machine.machine_id, e)

                uow.commit()

                # Publish cleanup event
                cleanup_event = ResourcesCleanedEvent(
                    aggregate_id="cleanup-operation",
                    aggregate_type="CleanupOperation",
                    resource_type="Multiple",
                    resource_id="all",
                    provider="system",
                    resource_count=requests_cleaned + machines_cleaned,
                    cleanup_reason=f"Cleanup all resources older than {command.older_than_days} days",
                )
                self.event_publisher.publish(cleanup_event)

                self.logger.info(
                    "Successfully cleaned up %s requests and %s machines",
                    requests_cleaned,
                    machines_cleaned,
                )

                return {
                    "success": True,
                    "requests_cleaned": requests_cleaned,
                    "machines_cleaned": machines_cleaned,
                    "total_cleaned": requests_cleaned + machines_cleaned,
                    "cutoff_date": cutoff_date.isoformat(),
                }

        except Exception as e:
            self.logger.error("Failed to cleanup all resources: %s", e)
            raise

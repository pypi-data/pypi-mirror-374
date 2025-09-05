"""Template repository implementation using storage strategy composition."""

from datetime import datetime
from typing import Any, Optional

from domain.template.aggregate import Template
from domain.template.repository import TemplateRepository as TemplateRepositoryInterface
from domain.template.value_objects import TemplateId
from infrastructure.error.decorators import handle_infrastructure_exceptions
from infrastructure.logging.logger import get_logger
from infrastructure.persistence.base.strategy import BaseStorageStrategy


class TemplateSerializer:
    """Handles Template aggregate serialization/deserialization."""

    def __init__(self, defaults_service=None) -> None:
        """Initialize the instance."""
        self.logger = get_logger(__name__)
        self.defaults_service = defaults_service

        # Get defaults service from DI container if not provided
        if not self.defaults_service:
            try:
                from domain.template.ports.template_defaults_port import (
                    TemplateDefaultsPort,
                )
                from infrastructure.di.container import get_container

                container = get_container()
                self.defaults_service = container.get(TemplateDefaultsPort)
            except Exception as e:
                self.logger.debug("Could not get defaults service from container: %s", e)

    @handle_infrastructure_exceptions(context="template_serialization")
    def to_dict(self, template: Template) -> dict[str, Any]:
        """Convert Template aggregate to dictionary with complete field support."""
        try:
            return {  # Core template fields
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "image_id": template.image_id,
                "instance_type": template.instance_type,
                "max_instances": template.max_instances,
                # Instance configuration
                "instance_types": template.instance_types,
                "primary_instance_type": template.primary_instance_type,
                # Network configuration
                "subnet_ids": template.subnet_ids,
                "security_group_ids": template.security_group_ids,
                "network_zones": template.network_zones,
                "public_ip_assignment": template.public_ip_assignment,
                # Storage configuration
                "root_volume_size": template.root_volume_size,
                "root_volume_type": template.root_volume_type,
                "root_volume_iops": template.root_volume_iops,
                "root_volume_throughput": template.root_volume_throughput,
                "storage_encryption": template.storage_encryption,
                "encryption_key": template.encryption_key,
                # Access and security
                "key_pair_name": template.key_pair_name,
                "user_data": template.user_data,
                "instance_profile": template.instance_profile,
                # Additional configuration
                "monitoring_enabled": template.monitoring_enabled,
                # Pricing and allocation
                "price_type": template.price_type,
                "allocation_strategy": template.allocation_strategy,
                "max_price": template.max_price,
                # Tags and metadata
                "tags": template.tags,
                "metadata": template.metadata,
                # Provider configuration
                "provider_type": template.provider_type,
                "provider_name": template.provider_name,
                "provider_api": template.provider_api,
                # Legacy HF fields (for backward compatibility)
                "vm_type": template.vm_type,
                "vm_types": template.vm_types,
                "key_name": template.key_name,
                # Status and timestamps
                "is_active": template.is_active,
                "created_at": (template.created_at.isoformat() if template.created_at else None),
                "updated_at": (template.updated_at.isoformat() if template.updated_at else None),
                # Schema version for migration support
                "schema_version": "2.0.0",
            }
        except Exception as e:
            self.logger.error("Failed to serialize template %s: %s", template.template_id, e)
            raise

    @handle_infrastructure_exceptions(context="template_deserialization")
    def from_dict(self, data: dict[str, Any]) -> Template:
        """Convert dictionary to Template aggregate with complete field support."""
        try:
            self.logger.debug("Converting template data: %s", data)

            # Apply configuration defaults BEFORE creating Template
            processed_data = data
            if self.defaults_service:
                try:
                    processed_data = self.defaults_service.resolve_template_defaults(
                        data, provider_instance_name="aws-default"
                    )
                    self.logger.debug("Applied configuration defaults to template data")
                except Exception as e:
                    self.logger.warning("Failed to apply defaults, using original data: %s", e)
                    processed_data = data

            # Parse datetime fields with defaults for legacy data
            now = datetime.now()
            created_at = (
                datetime.fromisoformat(processed_data["created_at"])
                if processed_data.get("created_at")
                else now
            )
            updated_at = (
                datetime.fromisoformat(processed_data["updated_at"])
                if processed_data.get("updated_at")
                else now
            )

            # Convert legacy format to new format
            template_id = processed_data.get("templateId", processed_data.get("template_id"))
            if not template_id:
                raise ValueError(f"No template_id found in data: {list(processed_data.keys())}")

            # Build template data with complete field support
            template_data = {
                # Core template fields
                "template_id": template_id,
                "name": processed_data.get("name", template_id),
                "description": processed_data.get("description"),
                "image_id": processed_data.get("imageId", processed_data.get("image_id")),
                "instance_type": processed_data.get("vmType", processed_data.get("instance_type")),
                "max_instances": processed_data.get(
                    "maxNumber", processed_data.get("max_instances", 1)
                ),
                # Instance configuration
                "instance_types": processed_data.get("instance_types", {}),
                "primary_instance_type": processed_data.get("primary_instance_type"),
                # Network configuration
                "subnet_ids": (
                    [processed_data.get("subnetId")]
                    if processed_data.get("subnetId")
                    else processed_data.get("subnet_ids", [])
                ),
                "security_group_ids": processed_data.get(
                    "securityGroupIds", processed_data.get("security_group_ids", [])
                ),
                "network_zones": processed_data.get("network_zones", []),
                "public_ip_assignment": processed_data.get("public_ip_assignment"),
                # Storage configuration
                "root_volume_size": data.get("root_volume_size"),
                "root_volume_type": data.get("root_volume_type"),
                "root_volume_iops": data.get("root_volume_iops"),
                "root_volume_throughput": data.get("root_volume_throughput"),
                "storage_encryption": data.get("storage_encryption"),
                "encryption_key": data.get("encryption_key"),
                # Access and security
                "key_pair_name": data.get("keyName", data.get("key_pair_name")),
                "user_data": data.get("user_data"),
                "instance_profile": data.get("instance_profile"),
                # Additional configuration
                "monitoring_enabled": data.get("monitoring_enabled"),
                # Pricing and allocation
                "price_type": data.get("price_type", "ondemand"),
                "allocation_strategy": data.get("allocation_strategy", "lowest_price"),
                "max_price": data.get("max_price"),
                # Tags and metadata
                "tags": data.get("tags", {}),
                "metadata": data.get("metadata", {}),
                # Provider configuration
                "provider_type": data.get("provider_type"),
                "provider_name": data.get("provider_name"),
                "provider_api": data.get("providerApi", data.get("provider_api")),
                # Legacy HF fields (for backward compatibility)
                "vm_type": data.get("vmType", data.get("vm_type")),
                "vm_types": data.get("vm_types", {}),
                "key_name": data.get("keyName", data.get("key_name")),
                # Status and timestamps
                "is_active": data.get("is_active", True),
                "created_at": created_at,
                "updated_at": updated_at,
            }

            self.logger.debug("Converted template_data keys: %s", list(template_data.keys()))

            # Create template using model_validate to handle all fields correctly
            template = Template.model_validate(template_data)

            return template

        except Exception as e:
            self.logger.error("Failed to deserialize template data: %s", e)
            raise


class TemplateRepositoryImpl(TemplateRepositoryInterface):
    """Template repository implementation using storage strategy composition."""

    def __init__(self, storage_strategy: BaseStorageStrategy) -> None:
        """Initialize repository with storage strategy."""
        self.storage_strategy = storage_strategy
        self.serializer = TemplateSerializer()
        self.logger = get_logger(__name__)

    @handle_infrastructure_exceptions(context="template_save")
    def save(self, template: Template) -> list[Any]:
        """Save template using storage strategy and return extracted events."""
        try:
            # Save the template
            template_data = self.serializer.to_dict(template)
            self.storage_strategy.save(str(template.template_id.value), template_data)

            # Extract events from the aggregate
            events = template.get_domain_events()
            template.clear_domain_events()

            self.logger.debug(
                "Saved template %s and extracted %s events",
                template.template_id,
                len(events),
            )
            return events

        except Exception as e:
            self.logger.error("Failed to save template %s: %s", template.template_id, e)
            raise

    @handle_infrastructure_exceptions(context="template_retrieval")
    def get_by_id(self, template_id: TemplateId) -> Optional[Template]:
        """Get template by ID using storage strategy."""
        try:
            data = self.storage_strategy.find_by_id(str(template_id.value))
            if data:
                return self.serializer.from_dict(data)
            return None
        except Exception as e:
            self.logger.error("Failed to get template %s: %s", template_id, e)
            raise

    @handle_infrastructure_exceptions(context="template_retrieval")
    def find_by_id(self, template_id: TemplateId) -> Optional[Template]:
        """Find template by ID (alias for get_by_id)."""
        return self.get_by_id(template_id)

    @handle_infrastructure_exceptions(context="template_search")
    def find_by_template_id(self, template_id: str) -> Optional[Template]:
        """Find template by template ID string."""
        try:
            return self.get_by_id(TemplateId(value=template_id))
        except Exception as e:
            self.logger.error("Failed to find template by template_id %s: %s", template_id, e)
            raise

    @handle_infrastructure_exceptions(context="template_search")
    def find_by_name(self, name: str) -> Optional[Template]:
        """Find template by name."""
        try:
            criteria = {"name": name}
            data_list = self.storage_strategy.find_by_criteria(criteria)
            if data_list:
                return self.serializer.from_dict(data_list[0])
            return None
        except Exception as e:
            self.logger.error("Failed to find template by name %s: %s", name, e)
            raise

    @handle_infrastructure_exceptions(context="template_search")
    def find_active_templates(self) -> list[Template]:
        """Find active templates."""
        try:
            criteria = {"is_active": True}
            data_list = self.storage_strategy.find_by_criteria(criteria)
            return [self.serializer.from_dict(data) for data in data_list]
        except Exception as e:
            self.logger.error("Failed to find active templates: %s", e)
            raise

    @handle_infrastructure_exceptions(context="template_search")
    def find_by_provider_api(self, provider_api: str) -> list[Template]:
        """Find templates by provider API."""
        try:
            criteria = {"provider_api": provider_api}
            data_list = self.storage_strategy.find_by_criteria(criteria)
            return [self.serializer.from_dict(data) for data in data_list]
        except Exception as e:
            self.logger.error("Failed to find templates by provider_api %s: %s", provider_api, e)
            raise

    @handle_infrastructure_exceptions(context="template_search")
    def find_all(self) -> list[Template]:
        """Find all templates."""
        try:
            all_data = self.storage_strategy.find_all()
            return [self.serializer.from_dict(data) for data in all_data.values()]
        except Exception as e:
            self.logger.error("Failed to find all templates: %s", e)
            raise

    def get_all(self) -> list[Template]:
        """Get all templates - alias for find_all for backward compatibility."""
        return self.find_all()

    @handle_infrastructure_exceptions(context="template_search")
    def search_templates(self, criteria: dict[str, Any]) -> list[Template]:
        """Search templates by criteria."""
        try:
            data_list = self.storage_strategy.find_by_criteria(criteria)
            return [self.serializer.from_dict(data) for data in data_list]
        except Exception as e:
            self.logger.error("Failed to search templates with criteria %s: %s", criteria, e)
            raise

    @handle_infrastructure_exceptions(context="template_deletion")
    def delete(self, template_id: TemplateId) -> None:
        """Delete template by ID."""
        try:
            self.storage_strategy.delete(str(template_id.value))
            self.logger.debug("Deleted template %s", template_id)
        except Exception as e:
            self.logger.error("Failed to delete template %s: %s", template_id, e)
            raise

    @handle_infrastructure_exceptions(context="template_existence_check")
    def exists(self, template_id: TemplateId) -> bool:
        """Check if template exists."""
        try:
            return self.storage_strategy.exists(str(template_id.value))
        except Exception as e:
            self.logger.error("Failed to check if template %s exists: %s", template_id, e)
            raise

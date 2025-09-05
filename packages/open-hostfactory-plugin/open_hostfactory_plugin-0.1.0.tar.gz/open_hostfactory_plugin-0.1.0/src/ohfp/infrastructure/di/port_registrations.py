"""Port adapter registrations for dependency injection."""

# Import configuration manager
from config.manager import get_config_manager
from domain.base.ports import (
    ConfigurationPort,
    ContainerPort,
    ErrorHandlingPort,
    EventPublisherPort,
    LoggingPort,
    SchedulerPort,
    TemplateConfigurationPort,
)
from domain.base.ports.spec_rendering_port import SpecRenderingPort
from infrastructure.adapters.error_handling_adapter import ErrorHandlingAdapter
from infrastructure.adapters.factories.container_adapter_factory import (
    ContainerAdapterFactory,
)
from infrastructure.template.configuration_manager import TemplateConfigurationManager


def register_port_adapters(container):
    """Register all port adapters in the DI container."""

    # Register configuration port with adapter
    def create_configuration_adapter(c):
        """Create configuration adapter bridging domain port to infrastructure manager."""
        from config.manager import get_config_manager
        from infrastructure.adapters.configuration_adapter import ConfigurationAdapter

        return ConfigurationAdapter(get_config_manager())

    container.register_singleton(ConfigurationPort, create_configuration_adapter)

    # Register UnitOfWorkFactory (abstract -> concrete mapping)
    # This was previously in _setup_core_dependencies but got lost during DI cleanup
    # Using consistent Base* naming pattern for abstract classes
    from domain.base import UnitOfWorkFactory as BaseUnitOfWorkFactory
    from infrastructure.adapters.logging_adapter import LoggingAdapter
    from infrastructure.utilities.factories.repository_factory import UnitOfWorkFactory

    config_manager = get_config_manager()
    container.register_instance(
        BaseUnitOfWorkFactory,
        UnitOfWorkFactory(config_manager, LoggingAdapter("unit_of_work")),
    )

    # Register logging port adapter
    container.register_singleton(LoggingPort, lambda c: LoggingAdapter("application"))

    # Register container port adapter using factory to avoid circular dependency
    container.register_singleton(ContainerPort, lambda c: ContainerAdapterFactory.create_adapter(c))

    # Register error handling port adapter
    container.register_singleton(ErrorHandlingAdapter, lambda c: ErrorHandlingAdapter())
    container.register_singleton(ErrorHandlingPort, lambda c: c.get(ErrorHandlingAdapter))

    # Register template configuration manager with manual factory (handles
    # optional dependencies)
    def create_template_configuration_manager(c):
        """Create template configuration manager with dependencies."""
        # Import here to avoid circular imports
        from application.services.provider_capability_service import (
            ProviderCapabilityService,
        )

        return TemplateConfigurationManager(
            config_manager=c.get(ConfigurationPort),
            scheduler_strategy=c.get(SchedulerPort),
            logger=c.get(LoggingPort),
            event_publisher=c.get_optional(EventPublisherPort),
            provider_capability_service=c.get_optional(ProviderCapabilityService),
        )

    container.register_singleton(
        TemplateConfigurationManager, create_template_configuration_manager
    )

    # Register template configuration port adapter
    from infrastructure.adapters.template_configuration_adapter import (
        TemplateConfigurationAdapter,
    )

    container.register_singleton(
        TemplateConfigurationAdapter,
        lambda c: TemplateConfigurationAdapter(
            template_manager=c.get(TemplateConfigurationManager),
            logger=c.get(LoggingPort),
        ),
    )
    container.register_singleton(
        TemplateConfigurationPort, lambda c: c.get(TemplateConfigurationAdapter)
    )

    # Register spec rendering port
    def create_spec_renderer(c):
        """Create Jinja spec renderer."""
        from infrastructure.template.jinja_spec_renderer import JinjaSpecRenderer

        return JinjaSpecRenderer(logger=c.get(LoggingPort))

    container.register_singleton(SpecRenderingPort, create_spec_renderer)

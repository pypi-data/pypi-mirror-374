"""Provider Strategy Application Layer - CQRS commands and queries for provider operations.

This package provides CQRS integration for the provider strategy pattern,
enabling runtime provider selection, health monitoring, and multi-cloud operations
through clean command/query interfaces.
"""

from .commands import (
    ConfigureProviderStrategyCommand,
    ExecuteProviderOperationCommand,
    RegisterProviderStrategyCommand,
    SelectProviderStrategyCommand,
    UpdateProviderHealthCommand,
)
from .queries import (
    GetProviderCapabilitiesQuery,
    GetProviderHealthQuery,
    GetProviderMetricsQuery,
    GetProviderStrategyConfigQuery,
    ListAvailableProvidersQuery,
)

__all__: list[str] = [
    "ConfigureProviderStrategyCommand",
    "ExecuteProviderOperationCommand",
    "GetProviderCapabilitiesQuery",
    # Queries
    "GetProviderHealthQuery",
    "GetProviderMetricsQuery",
    "GetProviderStrategyConfigQuery",
    "ListAvailableProvidersQuery",
    "RegisterProviderStrategyCommand",
    # Commands
    "SelectProviderStrategyCommand",
    "UpdateProviderHealthCommand",
]

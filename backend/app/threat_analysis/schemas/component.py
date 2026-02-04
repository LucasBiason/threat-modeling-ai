"""Component and architecture schemas."""

from enum import Enum

from pydantic import Field

from .base import BaseSchema


class ComponentType(str, Enum):
    """Types of architecture components."""

    USER = "User"
    CLIENT = "Client"
    SERVER = "Server"
    DATABASE = "Database"
    GATEWAY = "Gateway"
    LOAD_BALANCER = "LoadBalancer"
    CACHE = "Cache"
    QUEUE = "Queue"
    STORAGE = "Storage"
    API = "API"
    SERVICE = "Service"
    EXTERNAL_SERVICE = "ExternalService"
    OTHER = "Other"


class Component(BaseSchema):
    """A component in the architecture diagram."""

    id: str = Field(..., description="Unique identifier for the component")
    type: str = Field(..., description="Type of the component")
    name: str = Field(..., description="Display name of the component")
    description: str | None = Field(default=None, description="Optional description")


class Connection(BaseSchema):
    """A connection between two components."""

    from_id: str = Field(..., alias="from", description="Source component ID")
    to_id: str = Field(..., alias="to", description="Target component ID")
    protocol: str | None = Field(default=None, description="Communication protocol")
    description: str | None = Field(default=None, description="Connection description")
    encrypted: bool | None = Field(
        default=None, description="Whether connection is encrypted"
    )


class TrustBoundary(BaseSchema):
    """A trust boundary in the architecture."""

    name: str = Field(..., description="Name of the trust boundary")
    components: list[str] = Field(
        default_factory=list,
        description="Component IDs within this boundary",
    )


class DiagramData(BaseSchema):
    """Complete diagram analysis data."""

    model: str = Field(..., description="Model used for analysis")
    components: list[Component] = Field(
        default_factory=list,
        description="Detected components",
    )
    connections: list[Connection] = Field(
        default_factory=list,
        description="Detected connections",
    )
    boundaries: list[str] = Field(
        default_factory=list,
        description="Detected trust boundaries",
    )

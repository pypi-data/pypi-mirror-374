"""GDSFactory+ Pydantic models."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Literal, Self, TypeAlias

import pydantic as pyd
import sax

if TYPE_CHECKING:
    import kfactory as kf
    import numpy as np

    from gdsfactoryplus.settings import get_project_dir
else:
    from gdsfactoryplus.core.lazy import lazy_import

    np = lazy_import("numpy")
    kf = lazy_import("kfactory")
    get_project_dir = lazy_import("gdsfactoryplus.settings", "get_project_dir")


LogLevel: TypeAlias = Literal["debug", "info", "warning", "error"]

PdkType: TypeAlias = Literal["pdk", "base_pdk"]


class User(pyd.BaseModel):
    """A GDSFactory+ user."""

    user_name: str
    email: str
    organization_name: str | None
    organization_id: str | None
    pdks: list[str] | None
    is_superuser: bool


class SerializedComplexArray(pyd.BaseModel):
    """A serialized complex numpy array."""

    real: list[float]
    imag: list[float]

    def to_numpy(self) -> np.ndarray:
        """Convert to a complex number."""
        return np.array(self.real) + 1j * np.array(self.imag)

    @classmethod
    def from_numpy(cls, arr: sax.ComplexArray) -> Self:
        """Create from a complex numpy array."""
        npa = np.atleast_1d(np.asarray(arr, dtype=np.complex128))
        if npa.ndim != 1:
            msg = "Input array must be one-dimensional."
            raise ValueError(msg)
        return cls(real=np.real(npa).tolist(), imag=np.imag(npa).tolist())


SimulationResult: TypeAlias = dict[str, dict[str, sax.ComplexArray]]
SerializedSimulationResult: TypeAlias = dict[str, dict[str, SerializedComplexArray]]


class Simulation(pyd.BaseModel):
    """A SAX simulation configuration."""

    name: str
    layout: dict[str, Any]
    model: dict[str, Any]


class ModelRecord(pyd.BaseModel):
    """A model record for the database."""

    factory: str
    settings: str
    source: str | None
    pdk_type: PdkType = "pdk"

    def absolute_source(self) -> Path | None:
        """Return the absolute path to the source file."""
        if self.source is None:
            return None
        if Path(self.source).is_absolute():
            return Path(self.source).resolve()

        return (get_project_dir() / self.source).resolve()

    def to_db_tuple(self) -> tuple:
        """Convert to tuple for database insertion."""
        return (
            self.factory,
            self.settings,
            str(self.source) if self.source is not None else "",
            self.pdk_type,
        )

    def __hash__(self) -> int:
        """Return hash of the model record for deduplication."""
        return hash((self.factory, self.settings, self.source, self.pdk_type))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ModelRecord):
            return False
        return (
            self.factory == other.factory
            and self.settings == other.settings
            and self.source == other.source
            and self.pdk_type == other.pdk_type
        )


class FactoryRecord(pyd.BaseModel):
    """A factory record for the database."""

    name: str
    source: str | None
    status: str
    message: str
    default_settings: str = "{}"
    pdk_type: PdkType = "pdk"
    parents: str = "[]"
    children: str = "[]"
    is_partial: bool = False
    has_model: bool = False
    last_updated: str = ""  # Will be set automatically by database

    def absolute_source(self) -> Path | None:
        """Return the absolute path to the source file."""
        if self.source is None:
            return None
        if Path(self.source).is_absolute():
            return Path(self.source).resolve()

        return (get_project_dir() / self.source).resolve()

    def default_settings_dict(self) -> dict[str, Any]:
        """Return the default settings as a dictionary."""
        return json.loads(self.default_settings)

    def parents_list(self) -> list[str]:
        """Return the parents as a list."""
        return json.loads(self.parents)

    def children_list(self) -> list[str]:
        """Return the children as a list."""
        return json.loads(self.children)

    def to_db_tuple(self) -> tuple:
        """Convert to tuple for database insertion, excl. has_model and last_updated."""
        return (
            self.name,
            self.source,
            self.status,
            self.message,
            self.default_settings,
            self.pdk_type,
            self.parents,
            self.children,
            self.is_partial,
        )

    def __hash__(self) -> int:
        """Return hash of the factory record for deduplication."""
        return hash(
            (
                self.name,
                self.source,
                self.status,
                self.message,
                self.default_settings,
                self.pdk_type,
                self.parents,
                self.children,
                self.is_partial,
                self.has_model,
            )
        )

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, FactoryRecord):
            return False
        return (
            self.name == other.name
            and self.source == other.source
            and self.status == other.status
            and self.message == other.message
            and self.default_settings == other.default_settings
            and self.pdk_type == other.pdk_type
            and self.parents == other.parents
            and self.children == other.children
            and self.is_partial == other.is_partial
            and self.has_model == other.has_model
        )


class ComponentRecord(pyd.BaseModel):
    """A component record for the database."""

    name: str
    factory_name: str  # foreign key
    ports: str
    settings: str
    info: str

    def ports_list(self) -> list[str]:
        """Return the ports as a list."""
        return json.loads(self.ports)

    def settings_dict(self) -> dict[str, Any]:
        """Return the settings as a dictionary."""
        return json.loads(self.settings)

    def info_dict(self) -> dict[str, Any]:
        """Return the info as a dictionary."""
        return json.loads(self.info)

    def to_db_tuple(self) -> tuple:
        """Convert to tuple for database insertion."""
        return (
            self.name,
            self.factory_name,
            self.ports,
            self.settings,
            self.info,
        )

    def __hash__(self) -> int:
        """Return hash of the component record for deduplication."""
        return hash(
            (
                self.name,
                self.factory_name,
                self.ports,
                self.settings,
                self.info,
            )
        )

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ComponentRecord):
            return False
        return (
            self.name == other.name
            and self.factory_name == other.factory_name
            and self.ports == other.ports
            and self.settings == other.settings
            and self.info == other.info
        )

    @classmethod
    def from_tkcell(cls, tkcell: Any) -> Self:
        """Create a ComponentRecord from a TKCell object."""
        ports = object.__getattribute__(tkcell, "ports")
        port_names = json.dumps([str(p.name) for p in ports])
        factory_name = (
            getattr(tkcell, "basename", "")
            or getattr(tkcell, "function_name", "")
            or ""
        )
        default_settings = kf.KCellSettings()
        settings = getattr(tkcell, "settings", default_settings).model_dump_json()
        info = getattr(tkcell, "info", default_settings).model_dump_json()
        return cls(
            name=tkcell.name,
            factory_name=factory_name,
            ports=port_names,
            settings=settings,
            info=info,
        )


class Show3dMessage(pyd.BaseModel):
    """A message to vscode to show a 3D view."""

    what: Literal["show3D"] = "show3D"
    content: str

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash((self.what, self.content))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, Show3dMessage):
            return False
        return self.what == other.what and self.content == other.content


class ReloadSchematicMessage(pyd.BaseModel):
    """A message to vscode to trigger a schematic reload."""

    what: Literal["reloadSchematic"] = "reloadSchematic"
    path: str

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash((self.what, self.path))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ReloadSchematicMessage):
            return False
        return self.what == other.what and self.path == other.path


class ReloadFactoriesMessage(pyd.BaseModel):
    """A message to vscode to trigger a pics tree reload."""

    what: Literal["reloadFactories"] = "reloadFactories"

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash(self.what)

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ReloadFactoriesMessage):
            return False
        return self.what == other.what


class RestartServerMessage(pyd.BaseModel):
    """A message to vscode to trigger a server restart."""

    what: Literal["restartServer"] = "restartServer"

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash(self.what)

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, RestartServerMessage):
            return False
        return self.what == other.what


class ReloadLayoutMessage(pyd.BaseModel):
    """A message to vscode to trigger a gds viewer reload."""

    what: Literal["reloadLayout"] = "reloadLayout"
    cell: str

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash((self.what, self.cell))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ReloadLayoutMessage):
            return False
        return self.what == other.what and self.cell == other.cell


class LogMessage(pyd.BaseModel):
    """A message to vscode to log a message."""

    what: Literal["log"] = "log"
    level: LogLevel
    message: str
    source: str = "server"

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash((self.what, self.level, self.message))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, LogMessage):
            return False
        return (
            self.what == other.what
            and self.level == other.level
            and self.message == other.message
        )


class ParseSpiceRequest(pyd.BaseModel):
    """Request model for parsing SPICE files."""

    path: str
    flavor: str = "oc"


class ExportSpiceRequest(pyd.BaseModel):
    """Request model for exporting GDS files to SPICE format."""

    path: str
    flavor: str = "spectre"


class BboxRequest(pyd.BaseModel):
    """Request model for generating bounding box GDS files."""

    path: str
    outpath: str = ""
    layers_to_keep: list[str] = []
    bbox_layer: tuple[int, int] = (99, 0)
    ignore_ports: bool = False


class ShowBytesMessage(pyd.BaseModel):
    """A message to send raw bytes to the client."""

    what: Literal["showBytes"] = "showBytes"
    content: str  # base64 encoded content
    name: str | None = None

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash((self.what, self.content, self.name))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ShowBytesMessage):
            return False
        return (
            self.what == other.what
            and self.content == other.content
            and self.name == other.name
        )

    @classmethod
    def from_bytes(cls, content: bytes, name: str | None = None) -> Self:
        """Create a ShowBytesMessage from raw bytes."""
        encoded_content = base64.b64encode(content).decode()
        return cls(content=encoded_content, name=name)

    @classmethod
    def from_buf(cls, buf: BinaryIO, name: str | None = None) -> Self:
        """Create a ShowBytesMessage from a BytesIO buffer."""
        buf.seek(0)
        content = buf.read()
        return cls.from_bytes(content, name)


class ShowGdsMessage(pyd.BaseModel):
    """A message to vscode to show a GDS file."""

    what: Literal["showGds"] = "showGds"
    gds: str
    lyrdb: str | None = None

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash((self.what, self.gds, self.lyrdb))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ShowGdsMessage):
            return False
        self_path = str(Path(self.gds).resolve())
        other_path = str(Path(other.gds).resolve())
        self_lyrdb = None if self.lyrdb is None else str(Path(self.lyrdb).resolve())
        other_lyrdb = None if other.lyrdb is None else str(Path(other.lyrdb).resolve())
        return (
            self.what == other.what
            and self_path == other_path
            and self_lyrdb == other_lyrdb
        )


class DoItForMe(pyd.BaseModel):
    """DoItForMe Data."""

    prompt: str = ""
    initial_circuit: str = ""
    url: str = ""

    def __hash__(self) -> int:
        """Return hash of the DoItForMe message for deduplication."""
        return hash((self.prompt, self.initial_circuit, self.url))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, DoItForMe):
            return False
        return (
            self.prompt == other.prompt
            and self.initial_circuit == other.initial_circuit
            and self.url == other.url
        )


Message: TypeAlias = (
    LogMessage
    | ReloadFactoriesMessage
    | ReloadLayoutMessage
    | ReloadSchematicMessage
    | RestartServerMessage
    | Show3dMessage
    | ShowBytesMessage
    | ShowGdsMessage
)

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any

class BlacklistStatus(str, Enum):
    """Represents the blacklist status of the device."""
    CLEAN = "CLEAN"
    BLACKLISTED = "BLACKLISTED"


@dataclass
class Specifications:
    """Detailed technical hardware specifications of the mobile device."""
    cpu: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    screen_size: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["Specifications"]:
        """Parses a dictionary into a Specifications object."""
        if not data:
            return None
        return cls(
            cpu=data.get("cpu"),
            ram_gb=data.get("ram_gb"),
            storage_gb=data.get("storage_gb"),
            screen_size=data.get("screen_size"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the object back into a dictionary."""
        return asdict(self)


@dataclass
class ImeiCheckResponse:
    """Full technical specification and blacklist lookup report for an IMEI number."""
    imei: str
    brand: str
    model: str
    tac: str
    blacklist_status: BlacklistStatus
    carrier_lock: bool
    original_carrier: Optional[str] = None
    purchase_country: Optional[str] = None
    specifications: Optional[Specifications] = None
    
    # Queue / Pending Metadata
    status: Optional[str] = None
    history_id: Optional[int] = None
    ulid: Optional[str] = None
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImeiCheckResponse":
        """Parses an API JSON dictionary into an ImeiCheckResponse object."""
        # Convert blacklist_status safely to Enum
        blacklist_raw = data.get("blacklist_status", "CLEAN").upper()
        try:
            blacklist_status = BlacklistStatus(blacklist_raw)
        except ValueError:
            blacklist_status = BlacklistStatus.CLEAN  # Fallback

        # Check nested result block for history queries
        result_block = data.get("result", data) if data.get("result") is not None else data

        spec_data = result_block.get("specifications")
        specifications = Specifications.from_dict(spec_data) if spec_data else None

        # Determine status fallback
        status = data.get("status")
        if not status:
            status = "Pending" if "history_id" in data else "Done"

        return cls(
            imei=result_block.get("imei", ""),
            brand=result_block.get("brand", ""),
            model=result_block.get("model", ""),
            tac=result_block.get("tac", ""),
            blacklist_status=blacklist_status,
            carrier_lock=bool(result_block.get("carrier_lock", False)),
            original_carrier=result_block.get("original_carrier"),
            purchase_country=result_block.get("purchase_country"),
            specifications=specifications,
            status=status,
            history_id=data.get("history_id"),
            ulid=data.get("ulid"),
            message=data.get("message"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the object back into a dictionary (including nested objects)."""
        return asdict(self)

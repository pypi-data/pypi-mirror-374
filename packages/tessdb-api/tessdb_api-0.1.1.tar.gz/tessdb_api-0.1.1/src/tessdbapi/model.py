# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import re
from enum import Enum, auto
from datetime import datetime
from typing import Annotated, Optional, Self

# ---------------------
# Third party libraries
# ---------------------


from pydantic import BaseModel, AfterValidator, model_validator, EmailStr, HttpUrl

# -------------------
# Own package imports
# -------------------

from tessdbdao import (
    PhotometerModel,
    RegisterState,
    ObserverType,
)

# ---------
# Constants
# ---------

ZP_LOW = 10
ZP_HIGH = 30

OFFSET_LOW = 0
OFFSET_HIGH = 1

STARS4ALL_NAME_PATTERN = re.compile(r"^stars\d{1,7}$")

IMPOSSIBLE_TEMPERATURE = -273.15
IMPOSSIBLE_SIGNAL_STRENGTH = 99


class UnitsChoice(Enum):
    MQTT = auto()  # Units for readings comming from MQTT real Time
    GRAFANA = auto()  # Bulk import from Grafana
    LOGFILE = auto()  # Readings recovered by log file


# --------------------
# Validation functions
# --------------------


def is_mac_address(value: str) -> str:
    """'If this doesn't look like a MAC address at all, simple returns it.
    Otherwise properly formats it. Do not allow for invalid digits.
    """
    try:
        mac_parts = value.split(":")
        if len(mac_parts) != 6:
            raise ValueError("Invalid MAC: %s" % value)
        corrected_mac = ":".join(f"{int(x, 16):02X}" for x in mac_parts)
    except ValueError:
        raise ValueError("Invalid MAC: %s" % value)
    except AttributeError:
        raise ValueError("Invalid MAC: %s" % value)
    return corrected_mac


def is_valid_zp(value: float) -> float:
    if not (ZP_LOW <= value <= ZP_HIGH):
        raise ValueError(f"Zero Point {value} out of bounds [{ZP_LOW}-{ZP_HIGH}]")
    return value


def is_valid_offset(value: float) -> float:
    if not (OFFSET_LOW <= value <= OFFSET_HIGH):
        raise ValueError(f"Freq. Offset {value} out of bounds [{OFFSET_LOW}-{OFFSET_HIGH}]")
    return value


def is_longitude(value: float) -> float:
    if not (-180 <= value <= 180):
        raise ValueError(f"value {value} outside [-180,180] range")
    return value


def is_latitude(value: float) -> float:
    if not (-90 <= value <= 90):
        raise ValueError(f"value {value} outside [-90,90] range")
    return value


def is_azimuth(value: float) -> float:
    if not (-180 <= value <= 180):
        raise ValueError(f"value {value} outside [-180,180] range")
    return value


def is_altitude(value: float) -> float:
    if not (-90 <= value <= 90):
        raise ValueError(f"value {value} outside [-90,90] range")
    return value


def is_stars4all_name(value: str) -> str:
    matchobj = STARS4ALL_NAME_PATTERN.match(value)
    if not matchobj:
        raise ValueError(f"name {value} is not a legal STARS4ALL name")
    return value


def is_hash(value: str) -> str:
    if not (len(value) == 3 and value.lower().isalnum()):
        raise ValueError(f"hash {value} outside [A-Z1-9] range")
    return value

# --------------------
# Pydantic annotations
# --------------------

MacAddress = Annotated[str, AfterValidator(is_mac_address)]
ZeroPoint = Annotated[float, AfterValidator(is_valid_zp)]
FreqOffset = Annotated[float, AfterValidator(is_valid_offset)]
LongitudeType = Annotated[float, AfterValidator(is_longitude)]
LatitudeType = Annotated[float, AfterValidator(is_latitude)]
AzimuthType = Annotated[float, AfterValidator(is_azimuth)]
AltitudeType = Annotated[float, AfterValidator(is_altitude)]
Stars4AllName = Annotated[str, AfterValidator(is_stars4all_name)]
HashType = Annotated[str, AfterValidator(is_hash)]

# ---------------
# Pydantic models
# ---------------


class PhotometerInfo(BaseModel):
    name: str
    mac_address: MacAddress
    model: PhotometerModel
    firmware: Optional[str] = None
    registered: Optional[RegisterState] = RegisterState.AUTO
    authorised: bool
    zp1: ZeroPoint
    filter1: str
    offset1: FreqOffset
    zp2: Optional[ZeroPoint] = None
    filter2: Optional[str] = None
    offset2: Optional[FreqOffset] = None
    zp3: Optional[ZeroPoint] = None
    filter3: Optional[str] = None
    offset3: Optional[FreqOffset] = None
    zp4: Optional[ZeroPoint] = None
    filter4: Optional[str] = None
    offset4: Optional[FreqOffset] = None

    @model_validator(mode="after")
    def validate_zero_points(self) -> Self:
        if self.model == PhotometerModel.TESSW or self.model == PhotometerModel.TESSWDL:
            if self.zp1 is None:
                raise ValueError(f"For model {PhotometerModel.TESSW}, zp1 must not be None")
            if self.offset1 is None:
                raise ValueError(f"For model {PhotometerModel.TESSW}, offset1 must not be None")
            if self.filter1 is None:
                raise ValueError(f"For model {PhotometerModel.TESSW}, filter1 must not be None")
            if not all([self.zp2 is None, self.zp3 is None, self.zp4 is None]):
                raise ValueError(
                    f"For model {PhotometerModel.TESSW}, zp2, zp3, and zp4 must be None"
                )
            if not all([self.offset2 is None, self.offset3 is None, self.offset4 is None]):
                raise ValueError(
                    f"For model {PhotometerModel.TESSW}, offset2, offset3, and offset4 must be None"
                )
            if not all([self.filter2 is None, self.filter3 is None, self.filter4 is None]):
                raise ValueError(
                    f"For model {PhotometerModel.TESSW}, filter2, filter3, and filter4 must be None"
                )

        elif self.model == PhotometerModel.TESS4C:
            if None in [self.zp1, self.zp2, self.zp3, self.zp4]:
                raise ValueError(
                    f"For model {PhotometerModel.TESS4C}, zp1–zp4 must all be provided"
                )
            if None in [self.offset1, self.offset2, self.offset3, self.offset4]:
                raise ValueError(
                    f"For model {PhotometerModel.TESS4C}, offset1–offset4 must all be provided"
                )
            if None in [self.filter1, self.filter2, self.filter3, self.filter4]:
                raise ValueError(
                    f"For model {PhotometerModel.TESS4C}, filter1–filter4 must all be provided"
                )

        return self


class LocationInfo(BaseModel):
    longitude: LongitudeType
    latitude: LatitudeType
    height: Optional[float] = None
    place: str
    town: Optional[str] = None
    sub_region: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None


class ObserverInfo(BaseModel):
    type: ObserverType
    name: str
    affiliation: Optional[str] = None
    acronym: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    email: Optional[EmailStr] = None


class ReadingInfo(BaseModel):
    tstamp: datetime
    name: Stars4AllName
    sequence_number: int
    frequency: float  # Hz
    magnitude: float  # mag/arcsec^2
    box_temperature: float  # degrees celsius
    sky_temperature: float  # degrees celsius
    azimuth: Optional[AzimuthType] = None  # decimal degrees
    altitude: Optional[AltitudeType] = None  # decimal degrees
    longitude: Optional[LongitudeType] = None  # decimal degrees
    latitude: Optional[LatitudeType] = None  # decimal degrees
    elevation: Optional[float] = None  # meters above sea level
    signal_strength: Optional[int] = IMPOSSIBLE_SIGNAL_STRENGTH  # Tesstractor does not provide this
    hash: Optional[HashType] = None


class ReadingInfo4c(BaseModel):
    tstamp: datetime
    name: Stars4AllName
    sequence_number: int
    freq1: float  # Hz
    mag1: float  # mag/arcsec^2
    freq2: float  # Hz
    mag2: float  # mag/arcsec^2
    freq3: float  # Hz
    mag3: float  # mag/arcsec^2
    freq4: float  # Hz
    mag4: float  # mag/arcsec^2
    box_temperature: Optional[float] = (
        IMPOSSIBLE_TEMPERATURE  # TESS4C Early prototypes did not provide any temperature
    )
    sky_temperature: Optional[float] = (
        IMPOSSIBLE_TEMPERATURE  # TESS4C Early prototypes did not provide any temperature
    )
    azimuth: Optional[AzimuthType] = None  # decimal degrees
    altitude: Optional[AltitudeType] = None  # decimal degrees
    longitude: Optional[LongitudeType] = None  # decimal degrees
    latitude: Optional[LatitudeType] = None  # decimal degrees
    elevation: Optional[float] = None  # meters above sea level
    signal_strength: Optional[int] = IMPOSSIBLE_SIGNAL_STRENGTH  # Tesstractor does not provide this
    hash: Optional[HashType] = None


class ReferencesInfo(BaseModel):
    """Reading foreign references to other tables"""

    date_id: int
    time_id: int
    tess_id: int
    location_id: int
    observer_id: int
    units_id: int

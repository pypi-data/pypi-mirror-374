# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
from datetime import datetime
from typing import Optional, Tuple, Sequence, List, Callable
from functools import lru_cache

# -------------------
# Third party imports
# -------------------

from pubsub import pub


# from typing_extensions import Self
from sqlalchemy import select, and_
from tessdbdao import (
    TimestampSource,
    ReadingSource,
    ValidState,
)


from tessdbdao.noasync import Units, NameMapping, Tess, Tess4cReadings, TessReadings

# --------------
# local imports
# -------------

from ...util import Session
from ...model import UnitsChoice,  ReferencesInfo, ReadingInfo, ReadingInfo4c

# ----------------
# Global variables
# ----------------

log = logging.getLogger(__name__.split(".")[-1])

# ===================================
# Registry process auxiliar functions
# ===================================


def split_datetime(tstamp: datetime) -> Tuple[int, int]:
    """Round a timestamp to the nearest minute"""
    date_id = tstamp.year * 10000 + tstamp.month * 100 + tstamp.day
    time_id = tstamp.hour * 10000 + tstamp.minute * 100 + tstamp.second
    return date_id, time_id


# ------------------
# Auxiliar functions
# ------------------


class HashMismatchError(RuntimeError):
    """photometer hash mismatch error"""

    pass




@lru_cache(maxsize=10)
def resolve_units_id(session: Session, choice: UnitsChoice) -> int:
    """For readings recovery/batch uploads"""
    if choice == UnitsChoice.GRAFANA:
        target_timestamp_source = TimestampSource.PUBLISHER
        target_reading_source = ReadingSource.IMPORTED
    elif choice == UnitsChoice.LOGFILE:
        target_timestamp_source = TimestampSource.SUBSCRIBER
        target_reading_source = ReadingSource.IMPORTED
    else:
        target_timestamp_source = TimestampSource.SUBSCRIBER
        target_reading_source = ReadingSource.DIRECT
    query = select(Units.units_id).where(
        Units.timestamp_source == target_timestamp_source,
        Units.reading_source == target_reading_source,
    )
    return session.scalars(query).one()


def find_photometer_by_name(
    session: Session, name: str, mac_hash: str, tstamp: datetime, latest: bool
) -> Optional[Tess]:
    if latest:
        query = (
            select(Tess)
            .join(
                NameMapping,
                NameMapping.mac_address == Tess.mac_address,
            )
            .where(
                NameMapping.name == name,
                NameMapping.valid_state == ValidState.CURRENT,
                Tess.valid_state == ValidState.CURRENT,
            )
        )
    else:
        query = (
            select(Tess)
            .join(
                NameMapping,
                NameMapping.mac_address == Tess.mac_address,
            )
            .where(
                NameMapping.name == name,
                and_(NameMapping.valid_since <= tstamp, tstamp <= NameMapping.valid_until),
                and_(Tess.valid_since <= tstamp, tstamp <= Tess.valid_until),
                Tess.valid_state == ValidState.CURRENT,
            )
        )
    result = session.scalars(query).one_or_none()
    if result and mac_hash and mac_hash != "".join(result.mac_address.split(":"))[-3:-1]:
        raise HashMismatchError(mac_hash, result.mac_address)
    return result


def resolve_references(
    session: Session,
    reading: ReadingInfo,
    auth_filter: bool,
    latest: bool,
    units_choice: UnitsChoice,
) -> Optional[ReferencesInfo]:
    pub.sendMessage("nreadings")
    units_id = resolve_units_id(session, units_choice)
    try:
        phot = find_photometer_by_name(session, reading.name, reading.hash, reading.tstamp, latest)
        if phot is None:
            pub.sendMessage("rejNotRegistered")
            log.warning(
                "No TESS %s registered ! => %s",
                reading.name,
                dict(reading),
            )
            return None
    except HashMismatchError as e:
        pub.sendMessage("nreadings")
        log.error("photometer %s hash mismatch: %s", reading.name, str(e))
        return None
    else:
        if auth_filter and not phot.authorised:
            log.warning("[%s]: Not authorised: %s", reading.name, dict(reading))
            pub.sendMessage("rejNotAuthorised")
            return None
        date_id, time_id = split_datetime(reading.tstamp)
        return ReferencesInfo(
            date_id=date_id,
            time_id=time_id,
            tess_id=phot.tess_id,
            location_id=phot.location_id,
            observer_id=phot.observer_id,
            units_id=units_id,
        )


def resolve_references_seq(
    session: Session,
    readings: Sequence[ReadingInfo],
    auth_filter: bool,
    latest: bool,
    units_choice: UnitsChoice,
) -> List[Optional[ReferencesInfo]]:
    return [
        resolve_references(session, reading, auth_filter, latest, units_choice)
        for reading in readings
    ]


def tess_write_readings(
    session: Session,
    reading: ReadingInfo,
    reference: ReferencesInfo,
) -> None:
    db_reading = TessReadings(
        date_id=reference.date_id,
        time_id=reference.time_id,
        tess_id=reference.tess_id,
        location_id=reference.location_id,
        observer_id=reference.observer_id,
        units_id=reference.units_id,
        sequence_number=reading.sequence_number,
        frequency=reading.frequency,
        magnitude=reading.magnitude,
        box_temperature=reading.box_temperature,
        sky_temperature=reading.sky_temperature,
        azimuth=reading.azimuth,
        altitude=reading.altitude,
        longitude=reading.longitude,
        latitude=reading.latitude,
        elevation=reading.elevation,
        signal_strength=reading.signal_strength,
        hash=reading.hash,
    )
    session.add(db_reading)


def tess4c_write_readings(
    session: Session,
    reading: ReadingInfo4c,
    reference: ReferencesInfo,
) -> None:
    db_reading = Tess4cReadings(
        date_id=reference.date_id,
        time_id=reference.time_id,
        tess_id=reference.tess_id,
        location_id=reference.location_id,
        observer_id=reference.observer_id,
        units_id=reference.units_id,
        freq1=reading.freq1,
        mag1=reading.freq1,
        freq2=reading.freq2,
        mag2=reading.mag2,
        freq3=reading.freq3,
        mag3=reading.mag3,
        freq4=reading.freq4,
        mag4=reading.mag4,
        magnitude=reading.magnitude,
        box_temperature=reading.box_temperature,
        sky_temperature=reading.sky_temperature,
        azimuth=reading.azimuth,
        altitude=reading.altitude,
        longitude=reading.longitude,
        latitude=reading.latitude,
        elevation=reading.elevation,
        signal_strength=reading.signal_strength,
        hash=reading.hash,
    )
    session.add(db_reading)


def _photometer_looped_write(
    session: Session,
    readings: Sequence[ReadingInfo],
    references: Sequence[Optional[ReferencesInfo]],
    write_func: Callable[[Session, Sequence, Sequence], None],
):
    """One by one commit of database records"""
    for reading, reference in zip(readings, references):
        if reference:
            with session.begin():
                write_func(session, reading, reference)
                try:
                    session.flush()
                except Exception:
                    log.warning("Discarding reading by SQL Integrity error: %s", dict(reading))
                    session.rollback()
                else:
                    session.commit()


# ==================
# READING PROCESSING
# ==================


def photometer_batch_write(
    session: Session,
    readings: Sequence[ReadingInfo],
    write_func: Callable[[Session, Sequence, Sequence], None],
    auth_filter: bool,
    latest: bool,
    units_choice: UnitsChoice,
    dry_run: Optional[bool],
) -> None:
    session.begin()
    references = resolve_references_seq(
        session,
        readings,
        auth_filter,
        latest,
        units_choice,
    )
    for reading, reference in zip(readings, references):
        if reference:
            write_func(session, reading, reference)
    if dry_run:
        log.warning("Dry run mode. Database not written")
        session.rollback()
    else:
        try:
            session.flush()
        except Exception as e:
            log.error(e)
            log.warning("SQL Integrity error in block write. Looping one by one ...")
            session.rollback()
            session.close()
            _photometer_looped_write(session, readings, references, write_func)
        else:
            session.commit()
            session.close()


def tess_batch_write(
    session: Session,
    readings: Sequence[ReadingInfo],
    auth_filter: bool = False,
    latest: bool = False,
    units_choice: UnitsChoice = UnitsChoice.MQTT,
    dry_run: Optional[bool] = False,
) -> None:
    photometer_batch_write(
        session, readings, tess_write_readings, auth_filter, latest, units_choice, dry_run
    )


def tess4c_batch_write(
    session: Session,
    readings: Sequence[ReadingInfo],
    auth_filter: bool = False,
    latest: bool = False,
    units_choice: UnitsChoice = UnitsChoice.MQTT,
    dry_run: Optional[bool] = False,
) -> None:
    photometer_batch_write(
        session, readings, tess4c_write_readings, auth_filter, latest, units_choice, dry_run
    )

# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from functools import lru_cache

# -------------------
# Third party imports
# -------------------

from pubsub import pub


# from typing_extensions import Self
from sqlalchemy import func, select
from tessdbdao import (
    ObserverType,
    PhotometerModel,
    ValidState,
    RegisterOp,
    INFINITE_T,
)


from tessdbdao.noasync import Location, Observer, NameMapping, Tess

# --------------
# local imports
# -------------

from ...util import Session
from ...model import PhotometerInfo

ZP_EPS = 0.005
FREQ_EPS = 0.001

# ----------------
# Global variables
# ----------------

log = logging.getLogger(__name__.split(".")[-1])

# ===================================
# Registry process auxiliar functions
# ===================================


@lru_cache(maxsize=10)
def default_observer_id(session: Session) -> int:
    query = select(Observer.observer_id).where(
        Observer.type == ObserverType.ORG,
        func.lower(Observer.name) == "Unknown".lower(),
        Observer.valid_state == ValidState.CURRENT,
    )
    return session.scalars(query).one()


@lru_cache(maxsize=10)
def default_location_id(session: Session) -> int:
    query = select(Location.location_id).where(
        func.lower(Location.place) == "Unknown".lower(),
    )
    return session.scalars(query).one()


def observer_id_lookup(
    session: Session, obs_type: Optional[ObserverType], obs_name: Optional[str]
) -> int:
    observer_id = None
    if obs_type is not None and obs_name is not None:
        query = select(Observer.observer_id).where(
            Observer.type == obs_type,
            func.lower(Observer.name) == obs_name.lower(),
            Observer.valid_state == ValidState.CURRENT,
        )
        observer_id = session.scalars(query).one_or_none()
        if observer_id is None:
            log.warning("No observer id found for %s %s", obs_type, obs_name)
    return observer_id if observer_id is not None else default_observer_id(session)


def location_id_lookup(session: Session, place: Optional[str]) -> int:
    location_id = None
    if place is not None:
        query = select(Location.location_id).where(
            func.lower(Location.place) == place.lower(),
        )
        location_id = session.scalars(query).all()
        if not location_id:
            log.warning("No location id found for %s", place)
        elif len(location_id) > 1:
            log.warning("Found several location ids for %s. Choosing %d", place, location_id[0])
    return location_id[0] if location_id else default_location_id(session)


def find_photometer_by_name(session: Session, name: str) -> Optional[Tess]:
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
    return session.scalars(query).one_or_none()


def lookup_mac(session: Session, mac_address: str) -> Optional[NameMapping]:
    query = select(NameMapping).where(
        NameMapping.mac_address == mac_address, NameMapping.valid_state == ValidState.CURRENT
    )
    return session.scalars(query).one_or_none()


def lookup_name(session: Session, name: str) -> Optional[NameMapping]:
    query = select(NameMapping).where(
        NameMapping.name == name, NameMapping.valid_state == ValidState.CURRENT
    )
    return session.scalars(query).one_or_none()


def override_associations(
    session: Session,
    old_mac_entry: NameMapping,
    old_name_entry: NameMapping,
    candidate: PhotometerInfo,
    tstamp: datetime,
) -> None:
    old_mac_entry.valid_until = tstamp
    old_mac_entry.valid_state = ValidState.EXPIRED
    session.add(old_mac_entry)
    old_name_entry.valid_until = tstamp
    old_name_entry.valid_state = ValidState.EXPIRED
    session.add(old_name_entry)
    mapping = NameMapping(
        mac_address=candidate.mac_address,
        name=candidate.name,
        valid_since=tstamp,
        valid_until=INFINITE_T,
        valid_state=ValidState.CURRENT,
    )
    session.add(mapping)


def add_brand_new_tess(
    session: Session,
    candidate: PhotometerInfo,
    observer_type: Optional[ObserverType],
    observer_name: Optional[str],
    place: Optional[str],
    tstamp: datetime,
) -> None:
    observer_id = observer_id_lookup(session, observer_type, observer_name)
    location_id = location_id_lookup(session, place)
    photometer = Tess(
        mac_address=candidate.mac_address,
        valid_since=tstamp,
        valid_until=INFINITE_T,
        valid_state=ValidState.CURRENT,
        model=candidate.model,
        firmware=candidate.firmware,
        authorised=candidate.authorised,
        registered=candidate.registered,
        # From 1 to 4
        nchannels=4 if candidate.model == PhotometerModel.TESS4C else 1,
        zp1=candidate.zp1,
        filter1=candidate.filter1,
        offset1=candidate.offset1,
        zp2=candidate.zp2,
        filter2=candidate.filter2,
        offset2=candidate.offset2,
        zp3=candidate.zp3,
        filter3=candidate.filter3,
        offset3=candidate.offset3,
        zp4=candidate.zp4,
        filter4=candidate.filter4,
        offset4=candidate.offset4,
        location_id=location_id,
        observer_id=observer_id,
    )
    session.add(photometer)
    mapping = NameMapping(
        mac_address=candidate.mac_address,
        name=candidate.name,
        valid_since=tstamp,
        valid_until=INFINITE_T,
        valid_state=ValidState.CURRENT,
    )
    session.add(mapping)


def renaming_photometer(
    session: Session, old_mapping: NameMapping, candidate: PhotometerInfo, tstamp: datetime
) -> None:
    '''
    EXPIRE_EXISTING_MAC_SQL = """
    UPDATE name_to_mac_t SET valid_until = :eff_date, valid_state = :valid_expired
    WHERE  mac_address = :mac AND valid_state == :valid_current
    '''
    old_mapping.valid_until = tstamp
    old_mapping.valid_state = ValidState.EXPIRED
    mapping = NameMapping(
        mac_address=candidate.mac_address,
        name=candidate.name,
        valid_since=tstamp,
        valid_until=INFINITE_T,
        valid_state=ValidState.CURRENT,
    )
    session.add(old_mapping)
    session.add(mapping)


def replacing_photometer(
    session: Session, old_mapping: NameMapping, candidate: PhotometerInfo, tstamp: datetime
) -> None:
    old_mapping.valid_until = tstamp
    old_mapping.valid_state = ValidState.EXPIRED
    session.add(old_mapping)
    mapping = NameMapping(
        mac_address=candidate.mac_address,
        name=candidate.name,
        valid_since=tstamp,
        valid_until=INFINITE_T,
        valid_state=ValidState.CURRENT,
    )
    session.add(mapping)
    # Copy the observer and location from the broken photometer
    query = select(Tess.location_id, Tess.observer_id).where(
        Tess.mac_address == old_mapping.mac_address, Tess.valid_state == ValidState.CURRENT
    )
    location_id, observer_id = session.execute(query).one()
    photometer = Tess(
        mac_address=candidate.mac_address,
        valid_since=tstamp,
        valid_until=INFINITE_T,
        valid_state=ValidState.CURRENT,
        model=candidate.model,
        firmware=candidate.firmware,
        authorised=candidate.authorised,
        registered=candidate.registered,
        # From 1 to 4
        nchannels=4 if candidate.model == PhotometerModel.TESS4C else 1,
        zp1=candidate.zp1,
        filter1=candidate.filter1,
        offset1=candidate.offset1,
        zp2=candidate.zp2,
        filter2=candidate.filter2,
        offset2=candidate.offset2,
        zp3=candidate.zp3,
        filter3=candidate.filter3,
        offset3=candidate.offset3,
        zp4=candidate.zp4,
        filter4=candidate.filter4,
        offset4=candidate.offset4,
        location_id=location_id,
        observer_id=observer_id,
    )
    session.add(photometer)


def is_tess4c_changed(photometer: Tess, candidate: PhotometerInfo) -> bool:
    cand_zps = (candidate.zp1, candidate.zp2, candidate.zp3, candidate.zp4)
    phot_zps = (photometer.zp1, photometer.zp2, photometer.zp3, photometer.zp4)
    cand_off = (candidate.offset1, candidate.offset2, candidate.offset3, candidate.offset4)
    phot_off = (photometer.offset1, photometer.offset2, photometer.offset3, photometer.offset4)
    cand_fil = (candidate.filter1, candidate.filter2, candidate.filter3, candidate.filter4)
    phot_fil = (photometer.filter1, photometer.filter2, photometer.filter3, photometer.filter4)
    unchanged_zps = all([abs(x - y) < ZP_EPS for x, y in zip(cand_zps, phot_zps)])
    unchanged_off = all([abs(x - y) < FREQ_EPS for x, y in zip(cand_off, phot_off)])
    unchanged_fil = all(x == y for x, y in zip(cand_fil, phot_fil))
    if not unchanged_zps:
        log.info(
            "%s %s (%s) changing ZPs from %s to %s",
            candidate.model,
            candidate.name,
            candidate.mac_address,
            phot_zps,
            cand_zps,
        )
    if not unchanged_off:
        log.info(
            "%s %s (%s) changing Hz Offset from %s to %s",
            candidate.model,
            candidate.name,
            candidate.mac_address,
            phot_off,
            cand_off,
        )
    if not unchanged_fil:
        log.info(
            "%s %s (%s) changing Filters from %s to %s",
            candidate.model,
            candidate.name,
            candidate.mac_address,
            phot_fil,
            cand_fil,
        )
    return not all([unchanged_zps, unchanged_off, unchanged_fil])


def is_tessw_changed(photometer: Tess, candidate: PhotometerInfo) -> bool:
    cand_zps = (candidate.zp1,)
    phot_zps = (photometer.zp1,)
    cand_off = (candidate.offset1,)
    phot_off = (photometer.offset1,)
    unchanged_zps = all([abs(x - y) < ZP_EPS for x, y in zip(cand_zps, phot_zps)])
    unchanged_off = all([abs(x - y) < FREQ_EPS for x, y in zip(cand_off, phot_off)])
    if not unchanged_zps:
        log.info(
            "%s %s (%s) changing ZP from %s to %s",
            candidate.model,
            candidate.name,
            candidate.mac_address,
            phot_zps,
            cand_zps,
        )
    if not unchanged_off:
        log.info(
            "%s %s (%s) changing Hz Offset from %s to %s",
            candidate.model,
            candidate.name,
            candidate.mac_address,
            phot_off,
            cand_off,
        )
    return not all([unchanged_zps, unchanged_off])


def changed_managed_attributes(photometer: Tess, candidate: PhotometerInfo) -> bool:
    if candidate.model == PhotometerModel.TESS4C:
        return is_tess4c_changed(photometer, candidate)
    else:
        return is_tessw_changed(photometer, candidate)


def update_managed_attributes(
    session: Session, photometer: Tess, candidate: PhotometerInfo, tstamp: datetime
) -> None:
    photometer.valid_until = tstamp
    photometer.valid_state = ValidState.EXPIRED
    session.add(photometer)
    new_photometer = Tess(
        mac_address=candidate.mac_address,
        valid_since=tstamp,
        valid_until=INFINITE_T,
        valid_state=ValidState.CURRENT,
        model=candidate.model,
        firmware=photometer.firmware,  # carries over
        location_id=photometer.location_id,  # carries over
        observer_id=photometer.observer_id,  # carries over
        authorised=photometer.authorised,  # carries over
        registered=candidate.registered,
        # From 1 to 4
        nchannels=4 if candidate.model == PhotometerModel.TESS4C else 1,
        zp1=candidate.zp1,
        filter1=candidate.filter1,
        offset1=candidate.offset1,
        zp2=candidate.zp2,
        filter2=candidate.filter2,
        offset2=candidate.offset2,
        zp3=candidate.zp3,
        filter3=candidate.filter3,
        offset3=candidate.offset3,
        zp4=candidate.zp4,
        filter4=candidate.filter4,
        offset4=candidate.offset4,
    )
    session.add(new_photometer)
    # self.nZPChange += 1
    pub.sendMessage("ZP change")


def maybe_update_managed_attributes(
    session: Session, candidate: PhotometerInfo, tstamp: datetime
) -> None:
    photometer = find_photometer_by_name(session, candidate.name)
    if changed_managed_attributes(photometer, candidate):
        update_managed_attributes(session, photometer, candidate, tstamp)
    else:
        # self.nReboot += 1
        pub.sendMessage("Photometer reset")
        log.info(
            "Detected reboot for photometer %s (MAC = %s)", candidate.name, candidate.mac_address
        )


# ===================
# REGISTERING PROCESS
# ===================


def photometer_register(
    session: Session,
    candidate: PhotometerInfo,
    place: Optional[str] = None,
    observer_name: Optional[str] = None,
    observer_type: Optional[ObserverType] = None,
    tstamp: Optional[datetime] = None,
    dry_run: Optional[bool] = False,
) -> None:
    tstamp = tstamp or (datetime.now(timezone.utc) + timedelta(seconds=0.5)).replace(microsecond=0)
    old_mac_entry = lookup_mac(session, candidate.mac_address)
    old_name_entry = lookup_name(session, candidate.name)

    if not old_mac_entry and not old_name_entry:
        # Brand new TESS-W case:
        # No existitng (MAC, name) pairs in the name_to_mac_t table
        add_brand_new_tess(session, candidate, observer_type, observer_name, place, tstamp)
        # STATS CODE
        # self.nCreation += 1
        pub.sendMessage(RegisterOp.CREATE)
        log.info(
            "Brand new photometer registered: %s (MAC = %s)",
            candidate.name,
            candidate.mac_address,
        )
    elif old_mac_entry and not old_name_entry:
        # A clean rename with no collision
        # A (MAC, name) exists in the name_to_mac_t table with the MAC given by the candidate
        # but the name in the candidate does not.
        # STATS CODE
        # self.nRename += 1
        renaming_photometer(session, old_mac_entry, candidate, tstamp)
        pub.sendMessage(RegisterOp.RENAME)
        log.info(
            "Renamed photometer %s (MAC = %s) with brand new name %s",
            old_mac_entry.name,
            old_mac_entry.mac_address,
            candidate.name,
        )
    elif not old_mac_entry and old_name_entry:
        # Repairing a broken photometer
        # A (MAC, name) pair exist in the name_to_mac_t table with the same name as the candidate
        # but the MAC in the candiate is new.
        # This means that we are probably replacing a broken photometer with a new one, keeping the same name.
        # STATS CODE
        # self.nReplace += 1
        replacing_photometer(session, old_name_entry, candidate, tstamp)
        pub.sendMessage(RegisterOp.REPLACE)
        log.info(
            "Replaced photometer tagged %s (old MAC = %s) with new one with MAC %s",
            old_name_entry.name,
            old_name_entry.mac_address,
            candidate.mac_address,
        )
    else:
        # MAC not from the register message, but associtated to existing name
        # name not from from the register message, but assoctiated to to existing MAC
        # If the same MAC and same name remain, we must examine if there
        # is a change in the photometer managed attributes
        if (
            candidate.name == old_mac_entry.name
            and candidate.mac_address == old_name_entry.mac_address
        ):
            maybe_update_managed_attributes(session, candidate, tstamp)
        else:
            log.info(
                "Overridden associations (%s -> %s) and (%s -> %s) with new (%s -> %s) association data",
                old_mac_entry.name,
                old_mac_entry.mac_address,
                old_name_entry.name,
                old_name_entry.mac_address,
                candidate.name,
                candidate.mac_address,
            )
            log.warning("Label %s has no associated photometer now!", old_mac_entry.name)
            override_associations(session, old_mac_entry, old_name_entry, candidate, tstamp)
            pub.sendMessage(RegisterOp.EXTINCT)

    if dry_run:
        log.warning("Dry run mode. Database not written")
        session.rollback()

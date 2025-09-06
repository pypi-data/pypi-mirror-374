import pytest
import logging
from argparse import Namespace
from typing import List
from datetime import datetime, timezone

from sqlalchemy import select
from pydantic import ValidationError

from lica.sqlalchemy import sqa_logging

from tessdbdao.noasync import TessReadings

from tessdbapi.noasync.photometer.reading import ReadingInfo, UnitsChoice
from tessdbapi.noasync.photometer.reading import (
    resolve_references,
    tess_new,
    tess_batch_write,
)

from . import engine, Session
from ... import DbSize, copy_file

log = logging.getLogger(__name__.split(".")[-1])


# -------------------------------
# helper functions for test cases
# -------------------------------


def fetch_readings(session: Session) -> List[TessReadings]:
    query = select(TessReadings).order_by(TessReadings.date_id.asc(), TessReadings.time_id.asc())
    return session.scalars(query).all()


# ------------------
# Convenient fixtures
# -------------------


@pytest.fixture(scope="function", params=[DbSize.MEDIUM])
def database(request):
    args = Namespace(verbose=False)
    sqa_logging(args)
    copy_file(f"tess.{request.param}.db", "tess.db")
    yield Session()
    log.info("Teardown code disposes the engine")
    engine.dispose()


def test_reading_nonexists(database, stars8000r1):
    with database.begin():
        ref = resolve_references(
            session=database,
            reading=stars8000r1,
            auth_filter=False,
            latest=False,
            units_choice=UnitsChoice.LOGFILE,
        )
        assert ref is None

def test_reading_wrong_hash(database, stars1r1_wrong_hash):
    with database.begin():
        ref = resolve_references(
            session=database,
            reading=stars1r1_wrong_hash,
            auth_filter=False,
            latest=False,
            units_choice=UnitsChoice.LOGFILE,
        )
        assert ref is None

def test_reading_good_hash(database, stars1r1_good_hash):
    with database.begin():
        ref = resolve_references(
            session=database,
            reading=stars1r1_good_hash,
            auth_filter=False,
            latest=False,
            units_choice=UnitsChoice.LOGFILE,
        )
        assert ref is not None

def test_reading_authorization(database, stars100r1, stars1r1):
    with database.begin():
        ref = resolve_references(
            session=database,
            reading=stars1r1,
            auth_filter=True,
            latest=False,
            units_choice=UnitsChoice.LOGFILE,
        )
        assert ref is not None
        ref = resolve_references(
            session=database,
            reading=stars100r1,
            auth_filter=True,
            latest=False,
            units_choice=UnitsChoice.LOGFILE,
        )
        assert ref is None


def test_reading_write_1(database, stars1r1):
    with database.begin():
        ref = resolve_references(
            session=database,
            reading=stars1r1,
            auth_filter=False,
            latest=False,
            units_choice=UnitsChoice.LOGFILE,
        )
        if ref is not None:
            obj = tess_new(
                reading=stars1r1,
                reference=ref,
            )
            database.add(obj)
        database.commit()
    with database.begin():
        readings = fetch_readings(database)
    assert len(readings) == 1
    assert readings[0].sequence_number == 1


def test_reading_write_4(database, stars1_sparse):
    tess_batch_write(database, stars1_sparse)
    with database.begin():
        readings = fetch_readings(database)
    assert len(readings) == 4


def test_reading_write_dup(database, stars1_sparse, stars1_dense):
    tess_batch_write(database, stars1_sparse)
    with database.begin():
        readings = fetch_readings(database)
    assert len(readings) == 4
    tess_batch_write(database, stars1_dense)
    with database.begin():
        readings = fetch_readings(database)
    assert len(readings) == 10

def test_reading_write_dup2(database, stars1_sparse_dup):
    tess_batch_write(database, stars1_sparse_dup)
    with database.begin():
        readings = fetch_readings(database)
    assert len(readings) == 3

def test_reading_write_mixed(database, stars1_mixed):
    tess_batch_write(database, stars1_mixed)
    with database.begin():
        readings = fetch_readings(database)
    assert len(readings) == len(stars1_mixed) - 2

def test_valid_reading_1(database):
    with pytest.raises(ValidationError) as e:
        ReadingInfo(
            tstamp=datetime.now(timezone.utc).replace(microsecond=0),
            name=None,
            sequence_number=1,
            frequency=0,
            magnitude=0,
            box_temperature=0,
            sky_temperature=-10,
            signal_strength=-70,
        )
    log.info(e.value.errors())
    excp = e.value.errors()[0]
    assert excp["type"] == "string_type"
    assert excp["loc"][0] == "name"
    with pytest.raises(ValidationError) as e:
        ReadingInfo(
            tstamp=datetime.now(timezone.utc).replace(microsecond=0),
            name="foo",
            sequence_number=1,
            frequency=0,
            magnitude=0,
            box_temperature=0,
            sky_temperature=-10,
            signal_strength=-70,
        )
    log.info(e.value.errors())
    excp = e.value.errors()[0]
    assert excp["type"] == "value_error"
    assert excp["loc"][0] == "name"
    with pytest.raises(ValidationError) as e:
        ReadingInfo(
            tstamp=datetime.now(timezone.utc).replace(microsecond=0),
            name="stars1024",
            sequence_number=1,
            frequency=0,
            magnitude=0,
            box_temperature=0,
            sky_temperature=-10,
            signal_strength=-70,
            hash="GAGA",
        )
    log.info(e.value.errors())
    excp = e.value.errors()[0]
    assert excp["type"] == "value_error"
    assert excp["loc"][0] == "hash"
    with pytest.raises(ValidationError) as e:
        ReadingInfo(
            tstamp=datetime.now(timezone.utc).replace(microsecond=0),
            name="foo",
            sequence_number=1,
            frequency=0,
            magnitude=0,
            box_temperature=0,
            sky_temperature=-10,
            signal_strength=-70,
            hash="GAGA",
        )
    log.info(e.value.errors())
    excp = e.value.errors()
    assert excp[0]["type"] == "value_error"
    assert excp[0]["loc"][0] == "name"
    assert excp[1]["type"] == "value_error"
    assert excp[1]["loc"][0] == "hash"

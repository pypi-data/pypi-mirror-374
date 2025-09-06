import pytest
import logging
import shlex
import subprocess
from argparse import Namespace
from enum import StrEnum
from typing import List
from datetime import datetime, timezone

from sqlalchemy import select
from pydantic import ValidationError

from lica.sqlalchemy import sqa_logging

from tessdbdao.noasync import TessReadings, Tess4cReadings

from tessdbapi.noasync.photometer.reading import ReadingInfo, ReadingInfo4c, UnitsChoice
from tessdbapi.noasync.photometer.reading import (
    resolve_references,
    tess_write_readings,
    tess_batch_write,
)

from . import engine, Session

log = logging.getLogger(__name__.split(".")[-1])


class DbSize(StrEnum):
    SMALL = "anew"
    MEDIUM = "medium"
    LARGE = "big"


def copy_file(src: str, dst: str):
    cmd = shlex.split(f"cp -f {src} {dst}")
    log.info("copying %s into %s", src, dst)
    subprocess.run(cmd)


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


@pytest.fixture()
def stars8000r1(request) -> ReadingInfo:
    return ReadingInfo(
        tstamp=datetime(2025, 9, 4, 12, 34, 56, tzinfo=timezone.utc),
        name="stars8000",
        sequence_number=1,
        frequency=10,
        magnitude=23.4,
        box_temperature=12,
        sky_temperature=-12,
        signal_strength=-78,
    )


@pytest.fixture()
def stars1r1(request) -> ReadingInfo:
    return ReadingInfo(
        tstamp=datetime(2025, 9, 4, 12, 34, 56, tzinfo=timezone.utc),
        name="stars1",
        sequence_number=1,
        frequency=10,
        magnitude=23.4,
        box_temperature=12,
        sky_temperature=-12,
        signal_strength=-78,
    )


@pytest.fixture()
def stars100r1(request) -> ReadingInfo:
    return ReadingInfo(
        tstamp=datetime(2025, 9, 4, 12, 34, 56, tzinfo=timezone.utc),
        name="stars100",
        sequence_number=1,
        frequency=10,
        magnitude=23.4,
        box_temperature=12,
        sky_temperature=-12,
        signal_strength=-78,
    )


@pytest.fixture()
def stars1_dense(request) -> List[ReadingInfo]:
    return [
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 00, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=0,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 1, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=1,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 2, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=2,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 3, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=3,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 4, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=4,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 5, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=5,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 6, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=6,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 7, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=7,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 8, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=8,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 9, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=9,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
    ]


@pytest.fixture()
def stars1_sparse(request) -> List[ReadingInfo]:
    return [
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 2, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=2,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 3, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=3,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 5, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=5,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 7, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=7,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
    ]

@pytest.fixture()
def stars1_sparse_dup(request) -> List[ReadingInfo]:
    return [
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 2, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=2,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 3, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=3,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 3, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=3,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
        ReadingInfo(
            tstamp=datetime(2025, 9, 4, 00, 7, 00, tzinfo=timezone.utc),
            name="stars1",
            sequence_number=7,
            frequency=10,
            magnitude=23.4,
            box_temperature=12,
            sky_temperature=-12,
            signal_strength=-78,
        ),
    ]


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
            tess_write_readings(
                session=database,
                reading=stars1r1,
                reference=ref,
            )
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
    tess_batch_write(database, stars1_dense)
    with database.begin():
        readings = fetch_readings(database)
    assert len(readings) == 10

def test_reading_write_dup2(database, stars1_sparse_dup):
    tess_batch_write(database, stars1_sparse_dup)
    with database.begin():
        readings = fetch_readings(database)
    assert len(readings) == 3


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

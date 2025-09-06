import pytest
from enum import StrEnum
import logging
import shlex
import subprocess
from argparse import Namespace

from lica.sqlalchemy import sqa_logging

from tessdbapi.model import LocationInfo

from tessdbapi.noasync.location import location_lookup, location_create, location_update

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


@pytest.fixture(scope="function", params=[DbSize.MEDIUM])
def database(request):
    args = Namespace(verbose=False)
    sqa_logging(args)
    copy_file(f"tess.{request.param}.db", "tess.db")
    yield Session()
    log.info("Teardown code empty so far")
    engine.dispose()


def test_location_create_1(database):
    candidate = LocationInfo(
        longitude=-3.6124434,
        latitude=40.4208393,
        height=900,
        place="Melrose Place",
    )
    with database.begin():
        location_create(session=database, candidate=candidate)
        location = location_lookup(session=database, candidate=candidate)
        assert location.longitude == candidate.longitude
        assert location.latitude == candidate.latitude
        assert location.elevation == candidate.height
        assert location.country == "Spain"
        assert location.timezone == "Europe/Paris"


def test_location_create_2(database):
    candidate = LocationInfo(
        place="Melrose Place",
        longitude=-3.6124434,
        latitude=40.4208393,
        height=900,
    )
    with database.begin():
        location_create(session=database, candidate=candidate)
        location_create(session=database, candidate=candidate)


def test_location_update_1(database):
    candidate = LocationInfo(
        place="Melrose Place",
        longitude=-3.6124434,
        latitude=40.4208393,
        height=900,
    )
    with database.begin():
        location_create(session=database, candidate=candidate)
    log.info("Updating Location")
    candidate.height = 880
    candidate.timezone = "Europe/Madrid"
    with database.begin():
        location_update(session=database, candidate=candidate)
        location = location_lookup(session=database, candidate=candidate)
        location = location_lookup(session=database, candidate=candidate)
        assert location.longitude == candidate.longitude
        assert location.latitude == candidate.latitude
        assert location.elevation == candidate.height
        assert location.timezone == candidate.timezone

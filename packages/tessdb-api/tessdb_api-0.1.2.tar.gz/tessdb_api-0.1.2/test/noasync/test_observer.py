import pytest
import logging
import shlex
import subprocess
from argparse import Namespace
from enum import StrEnum

from pydantic import ValidationError

from lica.sqlalchemy import sqa_logging

from tessdbdao import ObserverType, ValidState
from tessdbapi.model import ObserverInfo

from tessdbapi.noasync.observer import (
    observer_lookup_current,
    observer_lookup_history,
    observer_create,
    observer_update,
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


@pytest.fixture(scope="function", params=[DbSize.MEDIUM])
def database(request):
    args = Namespace(verbose=False)
    sqa_logging(args)
    copy_file(f"tess.{request.param}.db", "tess.db")
    yield Session()
    log.info("Teardown code empty so far")
    engine.dispose()


def test_observer_1(database):
    candidate = ObserverInfo(
        type=ObserverType.ORG,
        name="Universidad Complutense de Madrid",
    )
    with database.begin():
        observer_create(session=database, candidate=candidate)
        observer = observer_lookup_current(session=database, candidate=candidate)
        assert observer.type == candidate.type
        assert observer.name == candidate.name
        assert observer.valid_state == ValidState.CURRENT

    with database.begin():
        observer_create(session=database, candidate=candidate)
        observer = observer_lookup_history(session=database, candidate=candidate)
        assert len(observer) == 1


def test_observer_2(database):
    candidate = ObserverInfo(
        type=ObserverType.ORG,
        name="Universidad Complutense de Madrid",
    )
    with database.begin():
        observer_create(session=database, candidate=candidate)
        observer_update(session=database, candidate=candidate, fix_current=False)
        observer = observer_lookup_history(session=database, candidate=candidate)
        assert len(observer) == 2
        assert observer[0].valid_state == ValidState.EXPIRED
        assert observer[1].valid_state == ValidState.CURRENT
        assert observer[0].valid_until == observer[1].valid_since


def test_observer_3(database):
    candidate = ObserverInfo(
        type=ObserverType.ORG,
        name="Universidad Complutense de Madrid",
        website_url="https://www.ucm.es",
        acronym="UCM",
    )
    with database.begin():
        observer_create(session=database, candidate=candidate)
        observer_update(session=database, candidate=candidate, fix_current=False)
        observer_update(session=database, candidate=candidate, fix_current=True)
        observer = observer_lookup_history(session=database, candidate=candidate)
        assert len(observer) == 2
        assert observer[-1].valid_state == ValidState.CURRENT
        assert observer[-1].website_url == str(candidate.website_url)
        assert observer[-1].acronym == candidate.acronym


def test_observer_excp():
    with pytest.raises(ValidationError) as excinfo:
        _ = ObserverInfo(type=ObserverType.ORG)
    log.info(excinfo.type)

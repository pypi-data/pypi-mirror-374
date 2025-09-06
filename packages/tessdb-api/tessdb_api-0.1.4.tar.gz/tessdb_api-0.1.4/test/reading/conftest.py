import pytest

from typing import List
from datetime import datetime, timezone


from tessdbapi.model import ReadingInfo

@pytest.fixture()
def stars8000r1() -> ReadingInfo:
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
def stars1r1() -> ReadingInfo:
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
def stars1r1_wrong_hash() -> ReadingInfo:
    return ReadingInfo(
        tstamp=datetime(2025, 9, 4, 12, 34, 56, tzinfo=timezone.utc),
        name="stars1",
        sequence_number=1,
        frequency=10,
        magnitude=23.4,
        box_temperature=12,
        sky_temperature=-12,
        signal_strength=-78,
        hash="ABC"
    )

@pytest.fixture()
def stars1r1_good_hash() -> ReadingInfo:
    return ReadingInfo(
        tstamp=datetime(2025, 9, 4, 12, 34, 56, tzinfo=timezone.utc),
        name="stars1",
        sequence_number=1,
        frequency=10,
        magnitude=23.4,
        box_temperature=12,
        sky_temperature=-12,
        signal_strength=-78,
        hash="95A"
    )

@pytest.fixture()
def stars100r1() -> ReadingInfo:
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
def stars1_dense() -> List[ReadingInfo]:
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
def stars1_sparse() -> List[ReadingInfo]:
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
def stars1_sparse_dup() -> List[ReadingInfo]:
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


 
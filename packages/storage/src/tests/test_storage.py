import os
from datetime import datetime
import pytest
import storage
from unittest import mock

feeds_stats = [
    {"feed_name": "test_feed_01", "dt": datetime.now(), "is_updated": 1},
    {"feed_name": "test_feed_02", "dt": datetime.now(), "is_updated": 1},
    {"feed_name": "test_feed_03", "dt": datetime.now(), "is_updated": 0},
]


@pytest.fixture(autouse=True)
def mock_env():
    with mock.patch.dict(
        os.environ,
        {"DB_URL": "localhost"},
    ):
        yield


class TestStorage:
    def test_to_tuple(self):
        result = storage.to_tuple(feeds_stats)
        assert isinstance(result, list)
        assert isinstance(result[0] and result[1] and result[2], tuple)

    def test_write_stats(self, mock_env):
        result = storage.write_stats(feeds_stats)
        assert result == 1

    # def test_write_ranks(self, mock_env):
    #     pass

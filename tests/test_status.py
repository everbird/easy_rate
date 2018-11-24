import pytest
import unittest
from unittest.mock import Mock, patch


from easy_rate.status import Status, get_value_by_dpath


class TestStatus(unittest.TestCase):

    def test_attr_access_with_schema(self):
        schema = {
            'a': '.Apple',
            'b': '.Banana',
            'c': '.Car.Dog',
        }
        data = {
            'Apple': 1,
            'Banana': 'yellow',
            'Car': {
                'Dog': True,
                'Egg': 0
            }
        }
        status = Status(schema, data)
        status.f = 'Fish'
        assert status.a == 1
        assert status.b == 'yellow'
        assert status.c == True
        assert status.f == 'Fish'

    @patch('easy_rate.status.fetch')
    def test_get_objs_by_urls(self, mock_fetch):
        URL_RESULT_DATA = {
            'http://localhost/a': {'Apple': 1},
            'http://localhost/b': {'Apple': 2},
        }
        async def f(*args, **kwargs):
            url = args[1]
            return URL_RESULT_DATA[url]

        mock_fetch.side_effect = f
        urls = [
            'http://localhost/a',
            'http://localhost/b'
        ]
        schema = {
            'a': '.Apple'
        }
        statuses = Status.get_objs_by_urls(urls, schema, 1)
        assert statuses[0].a == 1
        assert statuses[1].a == 2


def test_get_value_by_dpath():
    d = {
        'a': 1,
        'b': 2,
        'c': {
            'd': 'bingo!'
        }
    }
    assert 1 == get_value_by_dpath(d, '.a')
    assert 2 == get_value_by_dpath(d, '.b')
    assert 'bingo!' == get_value_by_dpath(d, '.c.d')

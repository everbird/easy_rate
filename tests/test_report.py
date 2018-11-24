import json
import pytest
import unittest
from unittest.mock import Mock

from easy_rate.report import RateReport, calculate_rate


class TestRateReport(unittest.TestCase):

    def setUp(self):
        self.mock_statuses = [
            Mock(a=1, b=2, c='Alice', d='ukulele'),
            Mock(a=3, b=8, c='Bob', d='ukulele'),
            Mock(a=1, b=10, c='Chris', d='guitar'),
            Mock(a=1, b=5, c='Alice', d='guitar'),
            Mock(a=1, b=5, c='Alice', d='guitar'),
        ]

    def test_rate_data(self):
        report = RateReport(self.mock_statuses, ['c', 'd'], 'b', 'a')
        assert report.rate_data == {
            ('Alice', 'ukulele'): 0.5,
            ('Alice', 'guitar'): 0.2,  # (1+1)/(5+5)
            ('Bob', 'ukulele'): 0.375,
            ('Chris', 'guitar'): 0.1,
        }

        report = RateReport(self.mock_statuses, 'd', 'b', 'a')
        assert report.rate_data == {
            'ukulele': 0.4,  # (1+3)/(2+8)
            'guitar': 0.15,  # (1+1+1)/(10+5+5)
        }

        report = RateReport(self.mock_statuses, ['c'], 'b', 'a')
        assert report.rate_data == {
            'Alice': 0.25,  # (1+1+1)/(2+5+5)
            'Bob': 0.375,
            'Chris': 0.1,
        }

    def test_render_dataset(self):
        report = RateReport(self.mock_statuses, ['c', 'd'], 'b', 'a')
        dataset = report.render_dataset(
            alias={
                'd': 'Instrument',
                'rate': 'Pass Rate'
            }
        )
        assert dataset.headers == ['c', 'Instrument', 'Pass Rate']

        r = dataset.export('json')
        assert json.loads(r) == [
            {
                'c': 'Alice',
                'Instrument': 'guitar',
                'Pass Rate': '20.00%',
            },
            {
                'c': 'Alice',
                'Instrument': 'ukulele',
                'Pass Rate': '50.00%',
            },
            {
                'c': 'Bob',
                'Instrument': 'ukulele',
                'Pass Rate': '37.50%',
            },
            {
                'c': 'Chris',
                'Instrument': 'guitar',
                'Pass Rate': '10.00%',
            },
        ]



def test_calculate_rate():
    mock_statuses = [
        Mock(a=1, b=2),
        Mock(a=3, b=8)
    ]

    assert 0.4 == calculate_rate(mock_statuses, 'b', 'a')

#!/usr/bin/python
# coding: utf8

import unittest
import pendulum

from flask import Flask, Response

from flask_dataview import RangeTimeSeries, FlaskDataViews


class MyTestSeries(RangeTimeSeries):
    def get_range(self):
        d1 = pendulum.datetime(2000, 1, 1, 12, 0)
        d2 = pendulum.datetime(2000, 1, 31, 12, 0)
        return (d1, d2)

    def get_data_range(self, dt_from, dt_to):
        out = []
        cur = dt_from.replace(microsecond=0)
        while cur < dt_to:
            val = ((cur.int_timestamp / 3600) % 24)
            out.append((cur.isoformat(), val))
            cur = cur.add(minutes=10)
        return out


class BaseTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    def test_base(self):
        e = FlaskDataViews()
        app = Flask("test_flask_app", template_folder=".")
        test_client = app.test_client()
        e.init_app(app)
        with app.app_context() as ctx:
            data = [MyTestSeries("temp"), MyTestSeries("hum")]
            chart = e.linechart("myid1", "My Chart", series=data)
            with app.test_request_context():
                self.assertIn("some_div_id", chart.render("some_div_id"))
                r = chart.data()
                self.assertTrue(isinstance(r, Response))
                self.assertEqual(r.status_code, 200)

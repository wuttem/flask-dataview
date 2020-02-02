#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pendulum
import random

from flask import Flask, render_template
from flask_dataview import FlaskDataViews, TimeSeries, RangeTimeSeries, Series


e = FlaskDataViews()
app = Flask(__name__, template_folder=".")
e.init_app(app)


class MySeries(RangeTimeSeries):
    def get_range(self):
        d1 = pendulum.now("utc").subtract(days=300)
        d2 = pendulum.now("utc")
        return (d1, d2)

    def get_data_range(self, dt_from, dt_to):
        out = []
        cur = dt_from.replace(microsecond=0)
        while cur < dt_to:
            val = ((cur.int_timestamp / 3600) % 24) + random.random() * 10
            out.append((cur.isoformat(), val))
            cur = cur.add(minutes=10)
        return out

class MySeries2(TimeSeries):
    def get_data(self):
        out = []
        cur = pendulum.now("utc").subtract(days=3).replace(microsecond=0)
        while cur < pendulum.now("utc"):
            val = ((cur.int_timestamp / 3600) % 24) + random.random() * 10
            out.append((cur.isoformat(), val))
            cur = cur.add(minutes=10)
        return out


@app.route('/', methods=['POST', 'GET'])
def home():
    data = [MySeries("temp"), MySeries("act"), MySeries("ph", active=False)]
    data2 = [MySeries2("temp", chart_type="bar"), MySeries2("act")]

    mychart = e.linechart("myid1", "My Chart", series=data)
    mychart2 = e.linechart("chartid2", "My Chart 2", series=data2)
    if mychart.is_post_request():
        return mychart.data()
    if mychart2.is_post_request():
        return mychart2.data()
    return render_template("template.html", chart=mychart, chart2=mychart2)


@app.route('/example2', methods=['POST', 'GET'])
def example2():
    some_series = Series(name="my series", data=[(x, x**2) for x in range(100)])
    mychart = e.linechart("myid3", "My quad chart", series=[some_series])
    if mychart.is_post_request():
        return mychart.data()
    return render_template("template.html", chart=mychart)
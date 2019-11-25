# flask-dataview

Dynamic Datatables and Timeseries Charts for Flask.

Used Libs:
- jquery
- jqueryui
- echarts
- datatables

## Example Charts

App:

```python
#!/usr/bin/python
# coding: utf8

import pendulum
import random

from flask import Flask, render_template
from flask_dataview import FlaskDataViews, TimeSeries


e = FlaskDataViews()
app = Flask(__name__, template_folder=".")
e.init_app(app)


class MySeries(TimeSeries):
    def get_range(self):
        d1 = pendulum.now("utc").subtract(days=300)
        d2 = pendulum.now("utc")
        return (d1, d2)

    def get_data(self, dt_from, dt_to):
        out = []
        cur = dt_from.replace(microsecond=0)
        while cur < dt_to:
            val = ((cur.int_timestamp / 3600) % 24) + random.random() * 10
            out.append((cur.isoformat(), val))
            cur = cur.add(minutes=10)
        return out


@app.route('/', methods=['POST', 'GET'])
def home():
    data = [MySeries("temp"), MySeries("act"), MySeries("ph", active=False)]
    mychart = e.linechart("My Chart", series=data)
    if mychart.is_post_request():
        return mychart.data()
    return render_template("template.html", chart=linechart)
```

Template HTML

```html
{{ jquery_cdn }}
{{ jquery_ui_cdn }}
{{ jquery_ui_css_cdn}}
{{ echarts_cdn }}

<link href="{{ url_for("echarts.echarts_css") }}" rel="stylesheet" />
<script src="{{ url_for("echarts.echarts_javascript") }}"></script>

<div id="mydivid" style="height: 400px;"></div>
{{ chart.render("mydivid") }}

```

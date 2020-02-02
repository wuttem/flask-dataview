# flask-dataview

Dynamic data visualizations for flask.
This Extension makes it easy to show large data in a flask application.
At the moment it only supports timeseries data and shows it in a line graph that can be dynamically zoomed and created.
Performance is really good because only the data that the user has selected is send and rendered.

Warning: This is a very (limited) premature version!

Used Libs:
- jquery
- bootstrap (for styling)
- echarts

## Installation

```bash
pip install flask-dataview
```

## Example Charts

App:

```python
#!/usr/bin/python
# coding: utf8

#!/usr/bin/python
# coding: utf8

import pendulum
import random

from flask import Flask, render_template
from flask_dataview import FlaskDataViews, RangeTimeSeries


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

@app.route('/', methods=['POST', 'GET'])
def home():
    data = [MySeries("temp"), MySeries("act"), MySeries("ph", active=False)]

    mychart = e.linechart("myid1", "My Chart", series=data)
    if mychart.is_post_request():
        return mychart.data()
    return render_template("template.html", chart=mychart)
```

Template HTML

```html
{{ jquery_cdn }}
{{ echarts_cdn }}
{{ dataview_javascript }}
{{ bootstrap3_cdn }}

<h1>Demo Charts</h1>

<div id="mydivid" style="height: 400px;"></div>
{{ chart.render("mydivid") }}

```
The subclass of `RangeTimeSeries` should implement `get_range` to return the full range of the data (minimum timestamp to maximum timestamp).
The method `get_data_range` should return the data in the selected timerange in tuples of isoformat timestamps and float values.


## Development Build / Upload
```
python setup.py sdist
twine upload dist/*
```

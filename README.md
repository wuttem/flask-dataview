# flask-dataview

Dynamic Datatables and Timeseries Charts for Flask.

Warning: This is a very (limited) premature version!

Used Libs:
- jquery
- bootstrap (for styling)
- echarts
- datatables

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
from flask_dataview import FlaskDataViews, RangeTimeSeries, Series


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

## Build / Upload
```
python setup.py sdist
twine upload dist/*
```

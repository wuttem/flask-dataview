#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pendulum
import uuid

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from flask import request, jsonify, current_app

from .helper import render_chart, update_mapping

class BaseChart(object):
    BASE_TOOLBOX = {
        "feature": {
            "dataZoom": {
                "yAxisIndex": 'none'
            },
            "restore": {},
            "saveAsImage": {}
        },
        "show": True,
        "right": "5%"
    }
    BASE_OPTIONS = {
        "title": {
            "left": "5%"
        },
        "useUTC": True,
        "tooltip": {"trigger": 'axis'},
        "legend": {
            "type": 'scroll',
        },
        "grid": {
            "left": "5%",
            "right": "5%",
            "top": 40,
        }
    }

    def __init__(self, id, title="", series=None, min_days=1, default_days=7,
                 max_days=30, context=None, initial_data=True, theme=None,
                 max_active_series=5, **kwargs):
        self._id = "{}.{}".format(self.__class__.__name__, id)
        self.dataset = DataSet(data=series, max_active_series=max_active_series)
        self.title = title
        self._theme = theme
        self.render_function = render_chart
        self._default_days = default_days
        self._min_days = min_days
        self._max_days = max_days
        self.context = {}
        self.initial_data = initial_data
        if context is not None:
            self.context.update(context)

    @property
    def ID(self):
        return self._id

    @property
    def theme(self):
        if self._theme is not None:
            return self._theme
        if current_app:
            if "dataview" in current_app.extensions:
                return current_app.extensions['dataview'].theme
        return None

    def is_post_request(self):
        if request.method == "POST":
            data = request.get_json()
            if data["action"] and data["chart_id"] == self.ID:
                self.handle_post_action(data)
                return True
        return False

    def enable_series(self, series_name):
        self.dataset.enable_series(series_name)

    def disable_series(self, series_name):
        self.dataset.disable_series(series_name)

    def handle_post_action(self, data):
        self.context.update(data)
        if "series" in data:
            for series_name in data["series"]:
                if data["series"][series_name]["active"]:
                    self.enable_series(series_name)
                else:
                    self.disable_series(series_name)

    def get_context_value(self, name, default=None):
        if name in self.context:
            return self.context[name]
        if default is not None:
            return default
        raise KeyError("context value {} not found".format(name))

    def get_url(self):
        return "{}".format(request.path)

    def get_value(self, name):
        if hasattr(self, name.upper()):
            return getattr(self, name.upper(), None)

    def add_series(self, s):
        self.dataset.add_data(s)

    def get_range_limits(self):
        return self.dataset.get_range_limits()

    def is_range_chart(self):
        l = self.get_range_limits()
        if l["min"] is not None and l["max"] is not None:
            return True
        return False

    def get_series_info(self):
        return self.dataset.get_series_info("all")

    def default_zoom_range(self):
        return self._default_days * 24 * 60 * 60 * 1000

    def min_zoom_range(self):
        return self._min_days * 24 * 60 * 60 * 1000

    def max_zoom_range(self):
        return self._max_days * 24 * 60 * 60 * 1000

    def get_range_information(self):
        if self.is_range_chart():
            l = self.get_range_limits()
            return {
                "range_chart": True,
                "ts_min": l["min"].int_timestamp * 1000,
                "ts_max": l["max"].int_timestamp * 1000,
                "default_ts_min": (l["max"].int_timestamp * 1000) - self.default_zoom_range(),
                "default_ts_max": l["max"].int_timestamp * 1000,
                "min_zoom_range": self.min_zoom_range(),
                "max_zoom_range": self.max_zoom_range(),
                "default_zoom_range": self.default_zoom_range()
            }
        return {
            "range_chart": False,
            "ts_min": None,
            "ts_max": None,
            "default_ts_min": None,
            "default_ts_max": None,
            "min_zoom_range": self.min_zoom_range(),
            "max_zoom_range": self.max_zoom_range(),
            "default_zoom_range": self.default_zoom_range()
        }

    def get_chart_series(self):
        out = []
        for series_name, ser in self.dataset.get_series_info("active").items():
            out.append({
                "name": ser["name"],
                "type": ser.get("chart_type", "line"),
                "smooth": False,
                #"areaStyle": {"color": "#ddd"},
                "showSymbol": False,
                "encode": {"x": 'idx', "y": ser["name"]}
            })
        return out

    def get_current_range(self):
        if not self.is_range_chart():
            return dict(min=None, max=None)
        limits = self.get_range_limits()
        d1 = None
        d2 = None
        r_d1 = self.get_context_value("from_date", False)
        r_d2 = self.get_context_value("to_date", False)
        if r_d1:
            d1 = pendulum.parse(r_d1)
        if r_d2:
            d2 = pendulum.parse(r_d2)

        if not d2 and limits["max"] is not None:
            d2 = limits["max"]
        if not d1 and d2:
            d1 = d2.subtract(seconds=self.default_zoom_range()/1000)
        return dict(min=d1, max=d2)

    def extend_data(self, real_data):
        source = real_data["source"]
        dims = real_data["dimensions"]
        if len(source) < 1:
            return real_data

        l = self.get_range_limits()
        assert dims[0] == "idx"
        first_d = tuple(source[0][1:])
        last_d = tuple(source[-1][1:])
        new_source = [(l["min"].isoformat(),) + first_d] + source + [(l["max"].isoformat(),) + last_d]
        return {"source": new_source, "dimensions": dims}

    def get_dataset(self):
        if self.is_range_chart():
            r = self.get_current_range()
            d = self.dataset.get_data(r["min"], r["max"])
            # extend
            d = self.extend_data(d)
        else:
            d = self.dataset.get_data()
        return d

    def build_options(self, with_data=True):
        base_opt = self.get_value("base_options")
        opt = {}
        update_mapping(opt, base_opt)
        build = {
            "title": {
                "text": self.title,
            },
            "dataset": self.get_dataset() if with_data else None,
            "toolbox": self.get_value("base_toolbox"),
            "yAxis": {"type": "value"},
            "series": self.get_chart_series()
        }

        idx_type = self.dataset.get_index_type()
        build["xAxis"] = {"type": idx_type}

        if idx_type == "time":
            build["xAxis"]["minInterval"] = 1 * 60 * 60 * 1000

        if self.is_range_chart():
            r = self.get_current_range()
            build["dataZoom"] = [{
                "type": "slider",
                "realtime": False,
                "filterMode": "empty",
                "showDataShadow": False,
                "startValue": r["min"].int_timestamp*1000,
                "endValue": r["max"].int_timestamp*1000,
                "minValueSpan": self.min_zoom_range(),
                "maxValueSpan": self.max_zoom_range(),
            }]
            build["grid"] = {"bottom": 80}
        update_mapping(opt, build)
        return opt

    def render(self, div_id):
        return self.render_function(self, div_id)

    def data(self):
        r = self.get_context_value("reload", False)
        out = {"reload": r}
        if r:
            out.update(self.build_options(with_data=True))
        else:
            out["dataset"] = self.get_dataset()
        return jsonify(out)


class DataSet():
    def __init__(self, data=None, max_active_series=100):
        self._data = []
        self.max_active_series = max_active_series
        self._dirty = True
        self._range_limit_cache = None
        self._data_cache = None
        for d in data:
            self.add_data(d)

    def add_data(self, d):
        if isinstance(d, TimeSeries):
            self._data.append(d)
        elif isinstance(d, Series):
            self._data.append(d)
        elif isinstance(d, list):
            self._data.append(Series.from_list(d))
        else:
            raise ValueError("invalid dataset entry")
        self.mark_dirty()

    def get_index_type(self):
        index_types = defaultdict(int)
        for s in self.series:
            if isinstance(s, TimeSeries):
                index_types["time"] += 1
            elif isinstance(s, CategorySeries):
                index_types["category"] += 1
            elif isinstance(s, Series):
                index_types["value"] += 1
        if len(index_types) == 0:
            return "category"
        if len(index_types) == 1:
            for t, i in index_types.items():
                if i == len(self.series):
                    return t
        raise ValueError("invalid series type mixes")

    @property
    def series(self):
        return self._data

    @property
    def active_series(self):
        out = [s for s in self.series if s.active]
        return out[:self.max_active_series]

    def enable_series(self, series_name):
        for s in self.series:
            if s.name == series_name:
                s.active = True
                self.mark_dirty()

    def disable_series(self, series_name):
        for s in self.series:
            if s.name == series_name:
                s.active = False
                self.mark_dirty()

    def mark_dirty(self):
        self._range_limit_cache = None
        self._data_cache = None

    def get_range_limits(self):
        if not self._range_limit_cache:
            d1 = None
            d2 = None
            for s in self.series:
                _d1, _d2 = s._get_range()
                if d1 is None:
                    d1 = _d1
                else:
                    d1 = min(d1, _d1)
                if d2 is None:
                    d2 = _d2
                else:
                    d2 = min(d2, _d2)
            self._range_limit_cache = dict(min=d1, max=d2)
        return self._range_limit_cache

    def get_series_info(self, select="all"):
        out = {}
        if select == "all":
            it = self.series
        elif select == "active":
            it = self.active_series
        else:
            raise ValueError("invalid series select")
        for s in it:
            out[s.name] = {"name": s.name, "active": s.active, "chart_type": s.chart_type}
        return out

    def get_data(self, min_range=None, max_range=None):
        if self._data_cache is None:
            series_count = len(self.active_series)
            series_names = []
            o = defaultdict(lambda: [None] * series_count)
            for i, s in enumerate(self.active_series):
                series_names.append(s.name)
                for idx, value in s._get_data(min_range, max_range):
                    o[idx][i] = value
            source = []
            dimensions = ["idx"] + series_names
            for j, dim in enumerate(o):
                line = [dim] + o[dim]
                source.append(line)
            self._data_cache = {"source": source, "dimensions": dimensions}
        return self._data_cache


class Series(metaclass=ABCMeta):
    def __init__(self, name, active=True, data=None, chart_type="line"):
        self.chart_type = chart_type
        self.name = name
        self.active = active
        if data is not None:
            self._static_data = self.data_from_list(data)

    def _get_range(self):
        if hasattr(self, "_static_range"):
            return self._static_range
        if hasattr(self, "get_range") and callable(self.get_range):
            return self.get_range()
        return (None, None)

    def _get_data(self, min, max):
        if hasattr(self, "_static_data"):
            return self._static_data
        if hasattr(self, "get_data_range") and callable(self.get_data_range):
            return self.get_data_range(min, max)
        return self.get_data()

    def get_data(self):
        raise RuntimeError("please overwrite get_data in Series subclass")

    @classmethod
    def data_from_list(cls, data_list):
        if not isinstance(data_list, list):
            raise ValueError("data must be in list format")
        # lets copy the data
        d = []
        for t in data_list:
            d.append(tuple(t))
        return d


class CategorySeries(Series):
    pass


class TimeSeries(Series):
    pass


class RangeTimeSeries(TimeSeries):
    def get_data(self):
        raise RuntimeError("get_data_range should be used in RangeTimeSeries")

    @abstractmethod
    def get_range(self):
        ...

    @abstractmethod
    def get_data_range(self):
        ...
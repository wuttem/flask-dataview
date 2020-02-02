#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import json

from flask import Blueprint, Response, Markup, render_template_string, send_file, make_response, url_for
from flask import current_app, _app_ctx_stack


from .helper import main_dir, lib_dir, template_dir, render_environment

logger = logging.getLogger(__name__)
view_bp = Blueprint("_dataview", __name__, url_prefix='/_dataview')


from .models import BaseChart, DataSet


def json_filter():
    def my_json(s):
        return Markup(json.dumps(s))
    def my_ppjson(s):
        return Markup(json.dumps(s, indent=4, sort_keys=True))
    return {"json": my_json, "ppjson": my_ppjson}


def add_echarts_javascript(html_str):
    js = g.get("echarts_js", None)
    if js is None:
        g.echarts_js = list()
    g.echarts_js.append(html_str)
    g.echarts_js = list(set(g.add_js))


def echarts_javascript_context():
    def my_javascript():
        js = g.get("echarts_js", None)
        if js is None:
            return Markup("")
        return Markup("\n".join(js))
    return {"echarts_javascript": my_javascript}


def cdn_tags_context():
    jquery = Markup('<script src="https://code.jquery.com/jquery-3.4.1.min.js" integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=" crossorigin="anonymous"></script>')
    jquery_ui = Markup('<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js" integrity="sha256-VazP97ZCwtekAsvgPBSUwPFKdrwD3unUfSGVYrahUqU=" crossorigin="anonymous"></script>')
    jquery_ui_css = Markup('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/themes/base/jquery-ui.min.css" integrity="sha256-sEGfrwMkIjbgTBwGLVK38BG/XwIiNC/EAG9Rzsfda6A=" crossorigin="anonymous" />')
    echarts = Markup('<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/4.3.0/echarts-en.min.js" integrity="sha256-0BLhrT+xIfvJO+8OfHf8iWMDzUmoL+lXNyswCl7ZUlY=" crossorigin="anonymous"></script>')
    dataview_javascript = Markup("<script src='{}'></script>".format(url_for("_dataview.dataview_javascript")))
    bootstrap3_css = Markup('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">')
    bootstrap3_js = Markup('<script src="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js" integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd" crossorigin="anonymous"></script>')
    bootstrap3 = Markup(bootstrap3_css + "\n" + bootstrap3_js)
    bootstrap4_css = Markup('<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">')
    bootstrap4_js = Markup('<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>')
    bootstrap4 = Markup(bootstrap4_css + "\n" + bootstrap4_js)
    return {"dataview_javascript": dataview_javascript, "jquery_cdn": jquery, "echarts_cdn": echarts, "bootstrap3_cdn": bootstrap3, "bootstrap4_cdn": bootstrap4, "bootstrap_cdn": bootstrap4}


class FlaskDataViews(object):
    def __init__(self, app=None, theme=None):
        self.app = app
        self.default_theme = theme
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('USE_CDN', False)
        app.config.setdefault('ECHARTS_THEME', self.default_theme)
        self.theme = app.config["ECHARTS_THEME"]
        # add routes
        app.register_blueprint(view_bp)

        # add filters
        for n, func in json_filter().items():
            app.jinja_env.filters[n] = func
            render_environment.filters[n] = func
        app.context_processor(echarts_javascript_context)
        app.context_processor(cdn_tags_context)

        # register
        app.extensions["dataview"] = self

        # add teardown
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        # do somthing on teardown ...

    def linechart(self, *args, **kwargs):
        if "theme" not in kwargs:
            return BaseChart(*args, theme=self.theme, **kwargs)
        return BaseChart(*args, **kwargs)

@view_bp.route('/echarts.min.js')
def echarts_lib_min():
    return send_file(os.path.join(lib_dir, "echarts", "js", "echarts.min.js"), mimetype='text/javascript')

@view_bp.route('/jquery.widget.js')
def jquery_widget():
    return send_file(os.path.join(lib_dir, "echarts", "js", "jquery.ui.widget.js"), mimetype='text/javascript')

@view_bp.route('/echarts.widget.js')
def echarts_widget():
    return send_file(os.path.join(lib_dir, "echarts", "js", "echarts.widget.js"), mimetype='text/javascript')

@view_bp.route('/flask_dataview.js')
def dataview_javascript():
    with open(os.path.join(lib_dir, "echarts", "js", "jquery.ui.widget.js"), 'r') as j_file1:
        with open(os.path.join(lib_dir, "echarts", "js", "jscolor.js"), 'r') as j_file2:
            with open(os.path.join(lib_dir, "echarts", "js", "echarts.widget.js"), 'r') as j_file3:
                full_js = j_file1.read() + "\n" + j_file2.read() + "\n" + j_file3.read()
                response = make_response(full_js)
                response.headers.set('Content-Type', 'text/javascript')
                return response

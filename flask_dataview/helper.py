#!/usr/bin/python
# coding: utf8

import os

from jinja2 import Environment, FileSystemLoader, Markup

main_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
lib_dir = os.path.join(main_dir, "flask_dataview", "static")
template_dir = os.path.join(main_dir, "flask_dataview", "templates")


render_environment = Environment(loader=FileSystemLoader(template_dir))


CDN_URLS = {
    "DATATABLES_CSS": "https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css",
    "DATATABLES_JS": "https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js",
    "JQUERY": "https://code.jquery.com/jquery-3.4.1.min.js"
}

def render_template(template_name, **kwargs):
    t = render_environment.get_template(template_name)
    return Markup(t.render(**kwargs))


def render_chart(chart, div_id, template="chart.html"):
    return render_template(template, chart_instance=chart, div_id=div_id)

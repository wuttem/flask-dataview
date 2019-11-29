function uniqId() {
    return Math.round(new Date().getTime() + (Math.random() * 100));
}

function timeAsUTCDate(dt) {
  var d = new Date(dt)
  var utc_ts = Date.UTC(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours(),
                        d.getMinutes(), d.getSeconds(), d.getMilliseconds())
  return utc_ts;
}

$.widget( "custom.etimeseries", {
    options: {
        theme: "default",
        data_url: null,
        show_series_select: true,
        max_range: null,
        default_range: null,
        data_range: null,
        chart_div:null,
        chart: null,
        dialog: null,
        is_range_chart: false,
        id: "unknown"
    },

    _adjust_options: function(options) {
      options["toolbox"]["feature"]["mySeriesTool"] = {
        show: true,
        title: 'Series Settings',
        icon: 'path://M8.2,38.4l-8.4,4.1l30.6,15.3L60,42.5l-8.1-4.1l-21.5,11L8.2,38.4z M51.9,30l-8.1,4.2l-13.4,6.9l-13.9-6.9L8.2,30l-8.4,4.2l8.4,4.2l22.2,11l21.5-11l8.1-4.2L51.9,30z M51.9,21.7l-8.1,4.2L35.7,30l-5.3,2.8L24.9,30l-8.4-4.1l-8.3-4.2l-8.4,4.2L8.2,30l8.3,4.2l13.9,6.9l13.4-6.9l8.1-4.2l8.1-4.1L51.9,21.7zM30.4,2.2L-0.2,17.5l8.4,4.1l8.3,4.2l8.4,4.2l5.5,2.7l5.3-2.7l8.1-4.2l8.1-4.2l8.1-4.1L30.4,2.2',
        onclick: this.open_settings.bind(this)};
      return options;
    },

    open_settings: function() {
      var body = this.options.dialog.find('.modal-body')
      body.empty();
      var content = jQuery('<div/>');
      var tab = jQuery('<table/>').addClass('table table-striped');
      var head = jQuery('<tr/>');
      head.append(jQuery('<th/>', {"text": "Show", "style": "width: 50px;"}));
      head.append(jQuery('<th/>', {"text": "Series"}));
      // head.append(jQuery('<th/>', {"text": "Color"}));
      tab.append(jQuery('<thead/>').append(head));
      $.each(this.options.series_info, function( key, value ) {
        var tr = jQuery('<tr/>');
        var td = jQuery('<td/>');
        var cb = jQuery('<input/>', {type: "checkbox", id: "cb_" + key, checked: value.active});
        cb.data("key", key);
        td.append(cb);
        tr.append(td);
        tr.append("<td>" + key + "</td>");
        // var color = jQuery('<input/>')[0];
        // var picker = new jscolor(color)
        // picker.fromHSV(360 / 100 * 10, 100, 100)
        // tr.append(jQuery('<td/>').append(color));
        tab.append(jQuery('<thead/>').append(tr));
      });
      content.append(tab);
      body.append(content);
      this.options.dialog.modal("show");
    },

    _save_dialog: function() {
      var d = this.options.dialog;
      var changed = false;
      var s = this.options.series_info;
      var r = this.options.data_range;
      d.find("input[type=checkbox]").each(function( index ) {
        var k = $( this ).data("key");
        var v = $( this )[0].checked;
        if (s[k].active != v)
        {
          changed = true;
          s[k].active = v;
        }
        console.log(s[k]);
      });
      if (changed) {
        setTimeout(this.load_data.bind(this, r[0], r[1], true), 10);
      }
      d.modal('hide');
    },

    reload: function() {
      var r = this.options.data_range;
      this.load_data(r[0], r[1], true);
    },

    _create_dialog: function() {
      var dialog_id = uniqId();
      var dialog = jQuery('<div/>', {
        "id": dialog_id,
        "class": 'modal fade echarts-dialog',
        "role": "dialog",
        "aria-labelledby": "myModalLabel"});
      var html = '<div class="modal-dialog" role="document">';
      html += '<div class="modal-content">';
      html += '<div class="modal-header">';
      html += '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>';
      html += '<h4 class="modal-title" id="myModalLabel">Chart Settings</h4>';
      html += '</div>';
      html += '<div class="modal-body">';
      html += 'fff';
      html += '</div>';
      html += '<div class="modal-footer">';
      html += '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';
      html += '<button type="button" class="btn btn-primary save-button">Save</button>';
      html += '</div>';
      html += '</div>';
      html += '</div>';
      dialog.html(html);
      var self = this;
      dialog.find('.save-button').on("click", function(e){
        e.preventDefault(); // prevent de default action
        self._save_dialog();
        //dialog.modal('hide');
      });
      dialog.modal("hide");
      return dialog;
    },

    _create: function() {
        var theme = this.options.theme;
        var show_series_select = this.options.show_series_select;
        var series_info = this.options.series_info;
        var l = this.options.limits;

        // Adjust Opt
        this.options.options = this._adjust_options(this.options.options)
        var o = this.options.options;

        var height = this.element.height();
        var chart_div = jQuery('<div/>', {
            "id": uniqId(),
            "class": 'etimeseries-chart',
            "style": "width: 100%;"});
        chart_div.height(height);

        var default_min = l.default_ts_min;
        var default_max = l.default_ts_max;
        this.options.max_range = [l.ts_min, l.ts_max];
        this.options.default_range = [default_min, default_max];
        this.options.data_range = [default_min, default_max];
        this.options.is_range_chart = l.range_chart;

        chart_div.appendTo(this.element);

        var dialog_div = this._create_dialog();
        this.options.dialog = dialog_div;

        if (this.options.theme != "default"){
          var chart = echarts.init(chart_div[ 0 ], this.options.theme);
        } else {
          var chart = echarts.init(chart_div[ 0 ]);
        }
        chart.setOption(o);

        // On Chart Zoom
        chart.on('dataZoom', this._handle_zoom.bind(this));

        // On Chart Reset
        chart.on('restore', this._handle_restore.bind(this));

        this.options.chart = chart;
        this.options.chart_div = chart_div;

        $(window).on('resize', function(){
            chart.resize();
        });
        setTimeout(function(){ chart.resize(); }, 50);
    },

    _handle_zoom: function (params) {
      var chart = this.options.chart;
      var axis = chart.getModel().option.xAxis[0];
      var d1 = new Date(axis.rangeStart);
      var d2 = new Date(axis.rangeEnd);

      // check if we are in max_range
      if (d1 < this.options.max_range[0]) {
        d1 = this.options.max_range[0];
      }
      if (d2 > this.options.max_range[1]) {
        d2 = this.options.max_range[1];
      }

      console.log("zoom", d1, d2);
      if (d1 < this.options.data_range[0] ||
          d2 > this.options.data_range[1])
      {
          this.load_data(d1, d2);
      }
    },

    _handle_restore: function (params) {
      var chart = this.options.chart;
      // var axis = chart.getModel().option.xAxis[0];
      var d1 = this.options.default_range[0];
      var d2 = this.options.default_range[1];
      console.log("restore", d1, d2);
      this.load_data(d1, d2);
    },

    load_data: function(f, t, reload=false) {
      var chart = this.options.chart;
      chart.showLoading();
      var f_value = new Date(f);
      //f_value.setHours(0,0,0,0);
      var t_value = new Date(t);
      //t_value.setHours(23,59,59,999);
      var f_iso = f_value.toISOString()//.substring(0, 10);
      var t_iso = t_value.toISOString()//.substring(0, 10);
      var req_url = this.options.data_url;
      var req_data = {from_date: f_iso, to_date: t_iso, action: "data",
                      chart_id: this.options.id, series: this.options.series_info,
                      "reload": reload};
      console.log("get_data", req_url);

      var self = this;
      $.ajax({
        type: "POST",
        url: req_url,
        data: JSON.stringify(req_data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){
          var opt = data;
          if (opt["reload"]) {
            self.options.options = self._adjust_options(opt)
            chart.clear();
            chart.setOption(self.options.options);
          } else {
            chart.setOption(opt);
          }
          self.options.data_range[0] = f;
          self.options.data_range[1] = t;
          chart.hideLoading();
        },
        failure: function(errMsg) {
            alert(errMsg);
        }
      });
    }
});
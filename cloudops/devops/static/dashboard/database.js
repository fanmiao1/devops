/**
 * Created by User on 2018/8/9.
 * 数据库资源状态
 */

function refresh() {
   range_trans(daterange);
}
function get_monitor_data(datetime_range='') {
    let num = echarts.init(document.getElementById('num'), 'macarons');
    let tps = echarts.init(document.getElementById('tps'), 'macarons');
    let qps = echarts.init(document.getElementById('qps'), 'macarons');
    let iops = echarts.init(document.getElementById('iops'), 'macarons');
    let recv_k = echarts.init(document.getElementById('recv_k'), 'macarons');
    let sent_k = echarts.init(document.getElementById('sent_k'), 'macarons');
    let com_insert = echarts.init(document.getElementById('com_insert'), 'macarons');
    let com_delete = echarts.init(document.getElementById('com_delete'), 'macarons');
    let com_update = echarts.init(document.getElementById('com_update'), 'macarons');
    let com_select = echarts.init(document.getElementById('com_read'), 'macarons');
    let inno_row_readed = echarts.init(document.getElementById('readed'), 'macarons');
    let inno_row_update = echarts.init(document.getElementById('updated'), 'macarons');
    let inno_row_delete = echarts.init(document.getElementById('deleted'), 'macarons');
    let inno_row_insert = echarts.init(document.getElementById('inserted'), 'macarons');
    let Inno_log_writes = echarts.init(document.getElementById('log'), 'macarons');
    let active_session = echarts.init(document.getElementById('active_session'), 'macarons');
    let total_session = echarts.init(document.getElementById('total_session'), 'macarons');
    let cpuusage = echarts.init(document.getElementById('cpu'), 'macarons');
    let memusage = echarts.init(document.getElementById('mem'), 'macarons');
    let ins_size = echarts.init(document.getElementById('size'), 'macarons');

    let daterange;
    let option = {
        tooltip: {
            trigger: 'axis'
        },
        title: [],
        legend: {
            show: true,
            selectedMode: 'multiple',
            orient: 'horizontal',
            type: 'scroll',
            x: 'right',
            y: 'bottom',
            bottom: 20,
        },
        toolbox: {
            show: true,
            feature: {
                mark: {show: true},
                dataZoom: {show: true},
                dataView: {show: true},
                magicType: {show: true, type: ['line', 'bar']},
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        dataZoom: {
            show: true,
            realtime: true,
            y: 36,
            height: 20,
            start: 0,
            end: 100
        },
        xAxis: [
            {
                type: 'time',
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: [],

    };
    $('#monitor_no_data').hide();
    $('#monitor_div_id').show();
    $('.my_monitor_line').show();
    num.clear();
    tps.clear();
    qps.clear();
    iops.clear();
    recv_k.clear();
    sent_k.clear();
    com_select.clear();
    com_insert.clear();
    com_delete.clear();
    com_update.clear();
    inno_row_readed.clear();
    inno_row_update.clear();
    inno_row_delete.clear();
    inno_row_insert.clear();
    Inno_log_writes.clear();
    active_session.clear();
    total_session.clear();
    cpuusage.clear();
    memusage.clear();
    ins_size.clear();
    let url = '/database/instance/monitor/get_monitor_data/';
    $.ajax({
        url: url,
        data: {'datetime_range': datetime_range},
        type: 'post',
        error: function (result) {
            $('#monitor_no_data').show();
            $('#monitor_div_id').hide();
        },
        success: function (monitor_res) {
            let num_datetime_list = monitor_res['num'];
            let tps_datetime_list = monitor_res['TPS'];
            let qps_datetime_list = monitor_res['QPS'];
            let iops_datetime_list = monitor_res['io'];
            let recv_k_datetime_list = monitor_res['recv_k'];
            let sent_k_datetime_list = monitor_res['sent_k'];
            let com_read_datetime_list = monitor_res['com_select'];
            let com_update_datetime_list = monitor_res['com_update'];
            let com_delete_datetime_list = monitor_res['com_delete'];
            let com_insert_datetime_list = monitor_res['com_insert'];
            let read_datetime_list = monitor_res['inno_row_readed'];
            let update_datetime_list = monitor_res['inno_row_update'];
            let delete_datetime_list = monitor_res['inno_row_delete'];
            let insert_datetime_list = monitor_res['inno_row_insert'];
            let log_datetime_list = monitor_res['Inno_log_writes'];
            let active_session_datetime_list = monitor_res['active_session'];
            let total_session_datetime_list = monitor_res['total_session'];
            let cpu_datetime_list = monitor_res['cpuusage'];
            let mem_datetime_list = monitor_res['memusage'];
            let size_datetime_list = monitor_res['ins_size'];

            let num_option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'line',
                    }
                },
                title: [],
                xAxis: {
                    type: 'category',
                    data: ['物理机', 'Aliyun', 'AWS', 'ECS']
                },
                yAxis: {
                    type: 'value'
                },
                series: [{
                    data: num_datetime_list,
                    type: 'bar',
                    barWidth: '30%',
                }]
            };
            let tps_option = JSON.parse(JSON.stringify(option));
            let qps_option = JSON.parse(JSON.stringify(option));
            let iops_option = JSON.parse(JSON.stringify(option));
            let recv_k_option = JSON.parse(JSON.stringify(option));
            let sent_k_option = JSON.parse(JSON.stringify(option));
            let com_read_option = JSON.parse(JSON.stringify(option));
            let com_update_option = JSON.parse(JSON.stringify(option));
            let com_delete_option = JSON.parse(JSON.stringify(option));
            let com_insert_option = JSON.parse(JSON.stringify(option));
            let read_option = JSON.parse(JSON.stringify(option));
            let update_option = JSON.parse(JSON.stringify(option));
            let delete_option = JSON.parse(JSON.stringify(option));
            let insert_option = JSON.parse(JSON.stringify(option));
            let log_option = JSON.parse(JSON.stringify(option));
            let active_session_option = JSON.parse(JSON.stringify(option));
            let total_session_option = JSON.parse(JSON.stringify(option));
            let cpu_option = JSON.parse(JSON.stringify(option));
            let mem_option = JSON.parse(JSON.stringify(option));
            let size_option = JSON.parse(JSON.stringify(option));

            num_option['title'].push({text: "Total Instance"});
            tps_option['title'].push({text: "TPS"});
            qps_option['title'].push({text: "QPS"});
            iops_option['title'].push({text: "每秒钟 IO 请求次数"});
            recv_k_option['title'].push({text: "每秒钟的输入流量(KB)"});
            sent_k_option['title'].push({text: "每秒钟的输出流量(KB)"});
            com_read_option['title'].push({text: "每秒钟 Select 执行数"});
            com_update_option['title'].push({text: "每秒钟 Update 执行数"});
            com_delete_option['title'].push({text: "每秒钟 Delete 执行数"});
            com_insert_option['title'].push({text: "每秒钟 Insert 执行数"});
            read_option['title'].push({text: "每秒钟读取行数"});
            update_option['title'].push({text: "每秒钟更新行数"});
            delete_option['title'].push({text: "每秒钟删除行数"});
            insert_option['title'].push({text: "每秒钟插入行数"});
            active_session_option['title'].push({text: "当前活跃连接数"});
            total_session_option['title'].push({text: "当前总连接数"});
            cpu_option['title'].push({text: "CPU 使用率(%)"});
            log_option['title'].push({text: "每秒钟日志写入次数"});
            mem_option['title'].push({text: "MEM 使用率(%)"});
            size_option['title'].push({text: "空间使用量(MB)"});

            tps_option['series'] = [];
            qps_option['series'] = [];
            iops_option['series'] = [];
            recv_k_option['series'] = [];
            sent_k_option['series'] = [];
            com_read_option['series'] = [];
            com_update_option['series'] = [];
            com_delete_option['series'] = [];
            com_insert_option['series'] = [];
            read_option['series'] = [];
            update_option['series'] = [];
            delete_option['series'] = [];
            insert_option['series'] = [];
            active_session_option['series'] = [];
            total_session_option['series'] = [];
            cpu_option['series'] = [];
            log_option['series'] = [];
            mem_option['series'] = [];
            size_option['series'] = [];

            for (let i in tps_datetime_list) {
                tps_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: tps_datetime_list[i],
                    }
                )
            }
            for (let i in qps_datetime_list) {
                qps_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: qps_datetime_list[i],
                    }
                )
            }
            for (let i in iops_datetime_list) {
                iops_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: iops_datetime_list[i],
                    }
                )
            }
            for (let i in recv_k_datetime_list) {
                recv_k_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: recv_k_datetime_list[i],
                    }
                )
            }
            for (let i in sent_k_datetime_list) {
                sent_k_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: sent_k_datetime_list[i],
                    }
                )
            }
            for (let i in com_read_datetime_list) {
                com_read_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: com_read_datetime_list[i],
                    }
                )
            }
            for (let i in com_update_datetime_list) {
                com_update_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: com_update_datetime_list[i],
                    }
                )
            }
            for (let i in com_delete_datetime_list) {
                com_delete_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: com_delete_datetime_list[i],
                    }
                )
            }
            for (let i in com_insert_datetime_list) {
                com_insert_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: com_insert_datetime_list[i],
                    }
                )
            }
            for (let i in read_datetime_list) {
                read_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: read_datetime_list[i],
                    }
                )
            }
            for (let i in update_datetime_list) {
                update_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: update_datetime_list[i],
                    }
                )
            }
            for (let i in delete_datetime_list) {
                delete_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: delete_datetime_list[i],
                    }
                )
            }
            for (let i in insert_datetime_list) {
                insert_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: insert_datetime_list[i],
                    }
                )
            }
            for (let i in log_datetime_list) {
                log_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: log_datetime_list[i],
                    }
                )
            }
            for (let i in active_session_datetime_list) {
                active_session_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: active_session_datetime_list[i],
                    }
                )
            }
            for (let i in total_session_datetime_list) {
                total_session_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: total_session_datetime_list[i],
                    }
                )
            }
            for (let i in cpu_datetime_list) {
                cpu_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: cpu_datetime_list[i],
                    }
                )
            }
            for (let i in mem_datetime_list) {
                mem_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: mem_datetime_list[i],
                    }
                )
            }
            for (let i in size_datetime_list) {
                size_option['series'].push(
                    {
                        name: i,
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        data: size_datetime_list[i],
                    }
                )
            }
            num.setOption(num_option, true);
            $('#num_line_loading_id').hide();
            tps.setOption(tps_option, true);
            $('#tps_line_loading_id').hide();
            qps.setOption(qps_option, true);
            $('#qps_line_loading_id').hide();
            iops.setOption(iops_option, true);
            $('#iops_line_loading_id').hide();
            recv_k.setOption(recv_k_option, true);
            $('#recv_k_line_loading_id').hide();
            sent_k.setOption(sent_k_option, true);
            $('#sent_k_line_loading_id').hide();
            com_select.setOption(com_read_option, true);
            $('#com_read_line_loading_id').hide();
            com_update.setOption(com_update_option, true);
            $('#com_update_line_loading_id').hide();
            com_delete.setOption(com_delete_option, true);
            $('#com_delete_line_loading_id').hide();
            com_insert.setOption(com_insert_option, true);
            $('#com_insert_line_loading_id').hide();
            inno_row_readed.setOption(read_option, true);
            $('#read_line_loading_id').hide();
            inno_row_update.setOption(update_option, true);
            $('#update_line_loading_id').hide();
            inno_row_delete.setOption(delete_option, true);
            $('#delete_line_loading_id').hide();
            inno_row_insert.setOption(insert_option, true);
            $('#insert_line_loading_id').hide();
            Inno_log_writes.setOption(log_option, true);
            $('#log_line_loading_id').hide();
            active_session.setOption(active_session_option, true);
            $('#active_session_line_loading_id').hide();
            total_session.setOption(total_session_option, true);
            $('#total_session_line_loading_id').hide();
            cpuusage.setOption(cpu_option, true);
            $('#cpu_line_loading_id').hide();
            memusage.setOption(mem_option, true);
            $('#mem_line_loading_id').hide();
            ins_size.setOption(size_option, true);
            $('#size_line_loading_id').hide();

        }
    });
     window.addEventListener("resize",function(){
         num.resize();
         tps.resize();
         qps.resize();
         iops.resize();
         recv_k.resize();
         sent_k.resize();
         com_select.resize();
         com_insert.resize();
         com_update.resize();
         com_delete.resize();
         inno_row_readed.resize();
         inno_row_update.resize();
         inno_row_delete.resize();
         inno_row_insert.resize();
         Inno_log_writes.resize();
         active_session.resize();
         total_session.resize();
         cpuusage.resize();
         memusage.resize();
         ins_size.resize();
    });
}
function range_trans(range){
  $("#range_div_id button").attr("class","ivu-btn ivu-btn-ghost");
  $("#range_"+range+"_id").attr("class","ivu-btn ivu-btn-primary");
  daterange = range;
  let ranges = {
      '最近1小时': [moment().subtract(1,'hours'), moment()],
      '今日': [moment().startOf('day'), moment()],
      '昨日': [moment().subtract(1,'days').startOf('day'), moment().subtract(1,'days').endOf('day')],
      '最近7日': [moment().subtract(6,'days'), moment()],
      '最近30日': [moment().subtract(29,'days'), moment()]
  };
  $('#my_monitor_1 span').html(ranges[range][0].format('YYYY-MM-DD HH:mm:ss') + ' ~ ' + ranges[range][1].format('YYYY-MM-DD HH:mm:ss'));
  get_monitor_data(ranges[range][0].format('YYYY-MM-DD HH:mm:ss') + ' ~ ' + ranges[range][1].format('YYYY-MM-DD HH:mm:ss'));
}

// 点击此标签触发加载
$("#top_dashboard div.ivu-tabs-tab:nth-child(7)").click(function(){
    $('#top_dashboard .dashboard_tab').hide();
    $('#dashboard_database_tab').show();
    //时间插件
  $('#my_monitor_1 span').html(moment().subtract(1 ,'hours').format('YYYY-MM-DD HH:mm:ss') + ' ~ ' + moment().format('YYYY-MM-DD HH:mm:ss'));
  daterange = '最近1小时';
  get_monitor_data($('#my_monitor_1 span').html());
  $('#my_monitor_1').daterangepicker({
      startDate: moment().subtract(1,'hours'),
      endDate: moment(),
      minDate: '01/07/2018',    //最小时间
      maxDate : moment(), //最大时间
      dateLimit : {
          days : 30
      }, //起止时间的最大间隔
      showDropdowns : true,
      showWeekNumbers : false, //是否显示第几周
      timePicker : true, //是否显示小时和分钟
      timePickerIncrement : 1, //时间的增量，单位为分钟
      timePicker24Hour : true, //是否使用24小时制来显示时间
      opens : 'left', //日期选择框的弹出位置
      buttonClasses : [ 'ivu-btn' ],
      applyClass : 'ivu-btn-primary',
      cancelClass : 'ivu-btn-ghost',
      format : 'YYYY-MM-DD HH:mm:ss', //控件中from和to 显示的日期格式
      separator : ' to ',
      locale : {
          format : 'YYYY-MM-DD HH:mm:ss',
          separator: ' ~ ',
          applyLabel : '确定',
          cancelLabel : '取消',
          fromLabel : '起始时间',
          toLabel : '结束时间',
          customRangeLabel : '自定义',
          daysOfWeek : [ '日', '一', '二', '三', '四', '五', '六' ],
          monthNames : [ '一月', '二月', '三月', '四月', '五月', '六月',
                  '七月', '八月', '九月', '十月', '十一月', '十二月' ],
          firstDay : 1
      }
  },
  function(start, end, label) {//格式化日期显示框
      $('#my_monitor_1 span').html(start.format('YYYY-MM-DD HH:mm:ss') + ' ~ ' + end.format('YYYY-MM-DD HH:mm:ss'));
      get_monitor_data(start.format('YYYY-MM-DD HH:mm:ss') + ' ~ ' + end.format('YYYY-MM-DD HH:mm:ss'));
  });
});
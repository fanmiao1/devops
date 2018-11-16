/**
 * Created by User on 2018/8/8.
 * 固定资产统计
 */
// 电脑出入库统计
function get_computer_flow_fun(start, end) {
  $('#line_asset_computer_amount_loading_id').show();
  $.ajax({
      type: "get",
      url: "/cmdb/daily_asset_flow_amount",
      dataType: "json",
      data: {'start_date': start, 'end_date': end},
      success: function(result) {
          var pie_flow_data = [
              {"name": "入库", "value": result['pie_flow_data']['入库']},
              {"name": "借出", "value": result['pie_flow_data']['借出']},
              {"name": "还回", "value": result['pie_flow_data']['还回']},
              {"name": "维修", "value": result['pie_flow_data']['维修']},
              {"name": "报废", "value": result['pie_flow_data']['报废']}
          ];
          pie_asset_computer_fun(pie_flow_data);
          line_asset_computer_fun(
              result['date_list'],
              result['line_in_count'],
              result['line_lend_count'],
              result['line_return_count'],
              result['line_maintain_count'],
              result['line_discard_count']
          )
      },
      complete: function() {
          $('#line_asset_computer_amount_loading_id').hide();
      }
  });
}

function get_server_amount_fun() {
    $('#table_expired_server_loading_id').show();
    $('#pie_asset_server_loading_id').show();
    $.ajax({
        url: '/opscenter/server/dashboard_asset_server_amount',
        type: 'get',
        success: function (result) {
            pie_asset_server_fun(result['name_list'], result['pie_data']);
            $('#expired_server_badge_count').html(result['expired_at_once_data'].length);
            $('#server_expire_at_one_table_tbody').html('');
            for (var v in result['expired_at_once_data']) {
                $('#server_expire_at_one_table_tbody').append('<tr>' +
                    '<td class="roll_x" style="text-align: center;color:#2d8cf0;">' + result['expired_at_once_data'][v][2] + '</td>' +
                    '<td class="roll_x" style="text-align: center;color:#2d8cf0;">' + result['expired_at_once_data'][v][1] + '</td>' +
                    '<td class="roll_x" style="text-align: center;">' + result['expired_at_once_data'][v][3] + '</td>' +
                    '<td class="roll_x" style="text-align: center;color:red;">' + result['expired_at_once_data'][v][0] + '</td>' +
                    '</tr>');
            }
        },
        complete: function () {
            $('#table_expired_server_loading_id').hide();
            $('#pie_asset_server_loading_id').hide();
        }
    });
}

function get_asset_amount_fun() {
    $('#table_expired_domain_loading_id').show();
    $('#pie_asset_domain_loading_id').show();
    $.ajax({
        url: '/cmdb/asset_amount',
        type: 'get',
        success: function (result) {
            $('#asset_card_computer_count').html(result['computer_count']);
            $('#asset_card_server_count').html(result['server_count']);
            $('#asset_card_cloud_server_count').html(result['all_server_count'] - result['server_count']);
            $('#asset_card_domain_count').html(result['domain_count']);
            $('#asset_card_net_count').html(result['net_asset_count']);
            $('#asset_card_printer_count').html(result['printer_count']);
            pie_asset_domain_fun(result['pie_domain_by_type_name_list'], result['pie_domain_by_type_data']);
            $('#expired_domain_badge_count').html(result['expired_at_once_data'].length);
            $('#asset_expire_at_one_table_tbody').html('');
            for (var v in result['expired_at_once_data']){
                $('#asset_expire_at_one_table_tbody').append('<tr>' +
                    '<td class="roll_x" style="text-align: center;color:#2d8cf0;">'+result['expired_at_once_data'][v][2]+'</td>' +
                    '<td class="roll_x" style="text-align: center;">'+result['expired_at_once_data'][v][0]+'</td>' +
                    '<td class="roll_x" style="text-align: center;color:red;">'+result['expired_at_once_data'][v][1]+'</td>' +
                    '</tr>');
            }
        },
        complete: function (){
            $('#table_expired_domain_loading_id').hide();
            $('#pie_asset_domain_loading_id').hide();
        }
    });
}

// 电脑出入库统计折线图
function line_asset_computer_fun(date_list, data1, data2, data3, data4, data5){
    var line_picture = echarts.init(document.getElementById('line_asset_computer_amount'), 'macarons');
    var option = {
      tooltip : {
          trigger: 'axis',
          position:function(p){   //其中p为当前鼠标的位置
              return [p[0] + 10, p[1] - 10];
          }
      },
      legend: {
          data:['入库', '借出', '还回', '维修', '报废']
      },
      xAxis: {
          type: 'category',
          data: date_list,
          axisLine:{
              lineStyle:{
                  color:'#000000'
              }
          }
      },
      yAxis: {
          type: 'value',
          axisLine:{
              lineStyle:{
                  color:'#000000'
              }
          }
      },
      series: [
          {
              name: '入库',
              data: data1,
              type: 'line',
              smooth: true,
              itemStyle: { normal: {label : {show: true}}}
          },
          {
              name: '借出',
              data: data2,
              type: 'line',
              smooth: true,
              itemStyle: { normal: {label : {show: true}}}
          },
          {
              name: '还回',
              data: data3,
              type: 'line',
              smooth: true,
              itemStyle: { normal: {label : {show: true}}}
          },
          {
              name: '维修',
              data: data4,
              type: 'line',
              smooth: true,
              itemStyle: { normal: {label : {show: true}}}
          },
          {
              name: '报废',
              data: data5,
              type: 'line',
              smooth: true,
              itemStyle: { normal: {label : {show: true}}}
          }
      ]
    };
    line_picture.setOption(option);
    window.addEventListener("resize",function(){
        line_picture.resize();
    });
}

// 电脑出入库统计饼图
function pie_asset_computer_fun(data) {
    var pie_picture = echarts.init(document.getElementById('pie_asset_computer_amount'), 'roma');
    var option = {
        title : {
            text: '电脑出入库统计',
            x:'center',
            show: false
        },
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: ['入库', '借出', '还回', '维修', '报废'],
            show: false
        },
        series : [
            {
                name: '电脑出入库统计',
                type: 'pie',
                radius : '55%',
                center: ['50%', '60%'],
                data: data,
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                },
                label: {
                    normal: {
                        formatter: '{b|{b}：}{c}  {per|{d}%}\n  ',
                        rich: {
                            a: {
                                color: '#999',
                                lineHeight: 15,
                                align: 'center'
                            },
                            b: {
                                fontSize: 12
                            },
                            per: {
                                color: '#eee',
                                backgroundColor: '#334455',
                                padding: [2, 4],
                                borderRadius: 2
                            }
                        }
                    }
                }
            }
        ]
    };
    pie_picture.setOption(option);
    window.addEventListener("resize",function(){
        pie_picture.resize();
    });
}

// 服务器分类统计饼图
function pie_asset_server_fun(data_name_list,data) {
    var pie_picture = echarts.init(document.getElementById('pie_asset_server_id'), 'roma');
    var option = {
        title : {
            text: '服务器分类统计',
            x:'center',
            show: false
        },
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: data_name_list,
            show: false
        },
        series : [
            {
                name: '服务商',
                type: 'pie',
                radius : '55%',
                center: ['50%', '60%'],
                data: data,
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                },
                label: {
                    normal: {
                        formatter: '{b|{b}：}{c}  {per|{d}%}\n  ',
                        rich: {
                            a: {
                                color: '#999',
                                lineHeight: 15,
                                align: 'center'
                            },
                            b: {
                                fontSize: 12
                            },
                            per: {
                                color: '#eee',
                                backgroundColor: '#334455',
                                padding: [2, 4],
                                borderRadius: 2
                            }
                        }
                    }
                }
            }
        ]
    };
    pie_picture.setOption(option);
    window.addEventListener("resize",function(){
        pie_picture.resize();
    });
}

// 域名统计饼图
function pie_asset_domain_fun(data_name_list,data) {
    var pie_picture = echarts.init(document.getElementById('pie_asset_domain_id'), 'roma');
    var option = {
        title : {
            text: '域名分类统计',
            x:'center',
            show: false
        },
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: data_name_list,
            show: false
        },
        series : [
            {
                name: '服务商',
                type: 'pie',
                radius : '55%',
                center: ['50%', '60%'],
                data: data,
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                },
                label: {
                    normal: {
                        formatter: '{b|{b}：}{c}  {per|{d}%}\n  ',
                        rich: {
                            a: {
                                color: '#999',
                                lineHeight: 15,
                                align: 'center'
                            },
                            b: {
                                fontSize: 12
                            },
                            per: {
                                color: '#eee',
                                backgroundColor: '#334455',
                                padding: [2, 4],
                                borderRadius: 2
                            }
                        }
                    }
                }
            }
        ]
    };
    pie_picture.setOption(option);
    window.addEventListener("resize",function(){
        pie_picture.resize();
    });
}

// 点击此标签触发加载
// $("#top_dashboard div.ivu-tabs-tab:nth-child(6)").click(function(){
//     $('#top_dashboard .dashboard_tab').hide();
//     $('#dashboard_asset_tab').show();
//     get_asset_amount_fun();
//     get_server_amount_fun();
//     get_computer_flow_fun(moment().subtract(6,'days').startOf('day').format('YYYY-MM-DD'), moment().format('YYYY-MM-DD'));
    // $('#asset_computer_amount_range span').html(moment().subtract(6,'days').startOf('day').format('YYYY-MM-DD') + ' ~ ' + moment().format('YYYY-MM-DD'));
    // $('#asset_computer_amount_range').daterangepicker({
    //   startDate: moment().subtract(6,'days').startOf('day'),
    //   endDate: moment(),
    //   minDate: '01/01/2017',    //最小时间
    //   maxDate : moment(), //最大时间
    //   showDropdowns : true,
    //   showWeekNumbers : false, //是否显示第几周
    //   timePicker : false, //是否显示小时和分钟
    //   timePickerIncrement : 1440, //时间的增量，单位为分钟
    //   timePicker12Hour : false, //是否使用12小时制来显示时间
    //   ranges : {
    //       //'最近1小时': [moment().subtract(1,'hours'), moment()],
    //       '今日': [moment().startOf('day'), moment()],
    //       '昨日': [moment().subtract(1,'days').startOf('day'), moment().subtract(1,'days').endOf('day')],
    //       '最近7日': [moment().subtract(6,'days'), moment()],
    //       '最近30日': [moment().subtract(29,'days'), moment()]
    //   },
    //   opens : 'left', //日期选择框的弹出位置
    //   buttonClasses : [ 'btn btn-default' ],
    //   applyClass : 'btn-small btn-primary',
    //   cancelClass : 'btn-small',
    //   format : 'YYYY-MM-DD', //控件中from和to 显示的日期格式
    //   separator : ' to ',
    //   locale : {
    //       applyLabel : '确定',
    //       cancelLabel : '取消',
    //       fromLabel : '起始时间',
    //       toLabel : '结束时间',
    //       customRangeLabel : '自定义',
    //       daysOfWeek : [ '日', '一', '二', '三', '四', '五', '六' ],
    //       monthNames : [ '一月', '二月', '三月', '四月', '五月', '六月',
    //               '七月', '八月', '九月', '十月', '十一月', '十二月' ],
    //       firstDay : 1
    //   }
    // },
    // function(start, end, label) {//格式化日期显示框
    //   $('#asset_computer_amount_range span').html(start.format('YYYY-MM-DD') + ' ~ ' + end.format('YYYY-MM-DD'));
    //   get_computer_flow_fun(start.format('YYYY-MM-DD'),end.format('YYYY-MM-DD'));
    // });
// });
/**
 * Created by User on 2018/8/7.
 * 工单统计
 */
function get_worksheet_count(start,end) {
  $('#worksheet_source_loading_id').show();
  $('#worksheet_all_count_loading_id').show();
  $('#worksheet_response_time_loading_id').show();
  $('#worksheet_solve_time_loading_id').show();
  var worksheet_line = echarts.init(document.getElementById('worksheet_line'), 'macarons');
  var worksheet_type_pie = echarts.init(document.getElementById('worksheet_type_pie'), 'roma');
  var worksheet_source_pie = echarts.init(document.getElementById('worksheet_source_pie'), 'roma');
  $.ajax({
      type: "post",
      url: "/get_worksheet_amount/",
      dataType: "json",
      data: {'start_date':start,'end_date':end},
      success: function(result) {
        var ws_date = [];
        var day_count_data = [];
        ws_date.push(result.date_list);
        day_count_data.push(result.day_count_list);

        // 工单响应时间统计
        $("#response_average").html(result.response_time_count.average);
        $("#response_one_hours").html("( "+ result.response_time_count.one_hours +" )");
        $("#response_one_to_eight_hours").html("( "+ result.response_time_count.one_to_eight_hours +" )");
        $("#response_eight_to_one_day").html("( "+ result.response_time_count.eight_to_one_day +" )");
        $("#response_more_than_one_day").html("( "+ result.response_time_count.more_than_one_day +" )");
        var response_one_hours = Math.round(result.response_time_count.one_hours/result.total_count*100);
        if (!response_one_hours){response_one_hours = 0}
        var response_one_to_eight_hours = Math.round(result.response_time_count.one_to_eight_hours/result.total_count*100);
        if (!response_one_to_eight_hours){response_one_to_eight_hours = 0}
        var response_eight_to_one_day = Math.round(result.response_time_count.eight_to_one_day/result.total_count*100);
        if (!response_eight_to_one_day){response_eight_to_one_day = 0}
        var response_more_than_one_day = Math.round(result.response_time_count.more_than_one_day/result.total_count*100);
        if (!response_more_than_one_day){response_more_than_one_day = 0}

        $('#response_one_hours_count_id').attr('data-transitiongoal', response_one_hours).progressbar();
        $('#response_one_to_eight_hours_count_id').attr('data-transitiongoal', response_one_to_eight_hours).progressbar();
        $('#response_eight_to_one_day_count_id').attr('data-transitiongoal', response_eight_to_one_day).progressbar();
        $('#response_more_than_one_day_count_id').attr('data-transitiongoal', response_more_than_one_day).progressbar();

        // 工单解决时间统计
        $("#solve_average").html(result.solve_time_count.average);
        $("#solve_one_hours").html("( "+ result.solve_time_count.one_hours +" )");
        $("#solve_one_to_eight_hours").html("( "+ result.solve_time_count.one_to_eight_hours +" )");
        $("#solve_eight_to_one_day").html("( "+ result.solve_time_count.eight_to_one_day +" )");
        $("#solve_more_than_one_day").html("( "+ result.solve_time_count.more_than_one_day +" )");
        //$('#through_flow_count_id').attr('data-transitiongoal', percent).progressbar({ display_text: 'fill' });
        var solve_one_hours = Math.round(result.solve_time_count.one_hours/result.total_count*100);
        if (!solve_one_hours){solve_one_hours = 0}
        var solve_one_to_eight_hours = Math.round(result.solve_time_count.one_to_eight_hours/result.total_count*100);
        if (!solve_one_to_eight_hours){solve_one_to_eight_hours = 0}
        var solve_eight_to_one_day = Math.round(result.solve_time_count.eight_to_one_day/result.total_count*100);
        if (!solve_eight_to_one_day){solve_eight_to_one_day = 0}
        var solve_more_than_one_day = Math.round(result.solve_time_count.more_than_one_day/result.total_count*100);
        if (!solve_more_than_one_day){solve_more_than_one_day = 0}

        $('#solve_one_hours_count_id').attr('data-transitiongoal', solve_one_hours).progressbar();
        $('#solve_one_to_eight_hours_count_id').attr('data-transitiongoal', solve_one_to_eight_hours).progressbar();
        $('#solve_eight_to_one_day_count_id').attr('data-transitiongoal', solve_eight_to_one_day).progressbar();
        $('#solve_more_than_one_day_count_id').attr('data-transitiongoal', solve_more_than_one_day).progressbar();

        //工单数量统计折线图
        worksheet_line_option = {
            tooltip : {
              trigger: 'axis',
              position:function(p){   //其中p为当前鼠标的位置
                  return [p[0] + 10, p[1] - 10];
              }
            },
            legend: {
              data:['工单数量']
            },
            xAxis: {
              type: 'category',
              data: eval(ws_date[0]),
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
            series: [{
              name: '工单数量',
              data: eval(day_count_data[0]),
              type: 'line',
              smooth: true,
              itemStyle: { normal: {label : {show: true}}}
            }]
        };
        //工单类型统计图饼
        var type_name_list = [];
        var type_data_list = [];
        for (var v in result.type_count){
            type_name_list.push(v);
            type_data_list.push({value:result.type_count[v], name:v})
        }
        type_option = {
            title : {
                x:'center'
            },
            tooltip : {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            series : [
                {
                    name: '类型',
                    type: 'pie',
                    radius : '55%',
                    center: ['50%', '60%'],
                    data: type_data_list,
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

        //工单来源统计图饼
        var source_name_list = [];
        var source_data_list = [];
        for (var i in result.source_count){
            source_name_list.push(i);
            source_data_list.push({value:result.source_count[i], name:i});
        }
        source_option = {
            title : {
                text: '工单来源',
                x:'center'
            },
            tooltip : {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            legend: {
                orient: 'vertical',
                left: 'left',
                data: source_name_list
            },
            series : [
                {
                    name: '工单来源',
                    type: 'pie',
                    radius : '55%',
                    center: ['50%', '60%'],
                    data: source_data_list,
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
        worksheet_line.setOption(worksheet_line_option);
        worksheet_type_pie.setOption(type_option);
        worksheet_source_pie.setOption(source_option);
      },
      complete: function () {
          $('#worksheet_source_loading_id').hide();
          $('#worksheet_all_count_loading_id').hide();
          $('#worksheet_response_time_loading_id').hide();
          $('#worksheet_solve_time_loading_id').hide();
      }
  });
    window.addEventListener("resize",function(){
      worksheet_line.resize();
      worksheet_type_pie.resize();
      worksheet_source_pie.resize();
    });
}

// $("#top_dashboard div.ivu-tabs-tab:nth-child(4)").click(function(){
//   $('#top_dashboard .dashboard_tab').hide();
//   $('#dashboard_worksheet_tab').show();
//   get_worksheet_count(moment().subtract(7 ,'days').format('YYYY-MM-DD'),moment().format('YYYY-MM-DD'))
//   //时间插件
//   $('#worksheet_num_range span').html(moment().subtract(7 ,'days').format('YYYY-MM-DD') + ' ~ ' + moment().format('YYYY-MM-DD'));
//
//   $('#worksheet_num_range').daterangepicker({
//       startDate: moment().startOf('day'),
//       endDate: moment(),
//       minDate: '01/01/2017',    //最小时间
//       maxDate : moment(), //最大时间
//       dateLimit : {
//           days : 30
//       }, //起止时间的最大间隔
//       showDropdowns : true,
//       showWeekNumbers : false, //是否显示第几周
//       timePicker : false, //是否显示小时和分钟
//       timePickerIncrement : 1440, //时间的增量，单位为分钟
//       timePicker12Hour : false, //是否使用12小时制来显示时间
//       ranges : {
//           //'最近1小时': [moment().subtract(1,'hours'), moment()],
//           '今日': [moment().startOf('day'), moment()],
//           '昨日': [moment().subtract(1,'days').startOf('day'), moment().subtract(1,'days').endOf('day')],
//           '最近7日': [moment().subtract(6,'days'), moment()],
//           '最近30日': [moment().subtract(29,'days'), moment()]
//       },
//       opens : 'left', //日期选择框的弹出位置
//       buttonClasses : [ 'btn btn-default' ],
//       applyClass : 'btn-small btn-primary',
//       cancelClass : 'btn-small',
//       format : 'YYYY-MM-DD', //控件中from和to 显示的日期格式
//       separator : ' to ',
//       locale : {
//           format : 'YYYY-MM-DD',
//           separator: ' ~ ',
//           applyLabel : '确定',
//           cancelLabel : '取消',
//           fromLabel : '起始时间',
//           toLabel : '结束时间',
//           customRangeLabel : '自定义',
//           daysOfWeek : [ '日', '一', '二', '三', '四', '五', '六' ],
//           monthNames : [ '一月', '二月', '三月', '四月', '五月', '六月',
//                   '七月', '八月', '九月', '十月', '十一月', '十二月' ],
//           firstDay : 1
//       }
//   },
//   function(start, end, label) {//格式化日期显示框
//       $('#worksheet_num_range span').html(start.format('YYYY-MM-DD') + ' ~ ' + end.format('YYYY-MM-DD'));
//       get_worksheet_count(start.format('YYYY-MM-DD'),end.format('YYYY-MM-DD'))
//   });
// });
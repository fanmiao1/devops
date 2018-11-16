/**
 * Created by User on 2018/8/7.
 * 工作流统计
 */
// 卡片、项目饼图、执行状态饼图的数据
function get_all_workflow_amount(){
    $('#workflow_project_source_loading_id').show();
    $('#workflow_exec_status_loading_id').show();
    $.ajax({
        url: '/flow/get_all_workflow_amount',
        type: 'get',
        success: function(result) {
            $('#workflow_project_flow_count').html(result['project_flow_count']['all']);
            $('#workflow_project_releaseflow_count').html(result['project_releaseflow_count']['all']);
            $('#workflow_database_release_count').html(result['database_release_count']['all']);
            $('#workflow_project_userflow_count').html(result['project_userflow_count']['all']);
            $('#workflow_cronflow_count').html(result['cronflow_count']['all']);
            pie_workflow_project_fun([
                {'name':'自建项目', 'value':result['project_flow_count']['自建项目']},
                {'name':'外购项目', 'value':result['project_flow_count']['外购项目']}
            ]);
            var data1 = [
                {'name': '已完成', 'value': result['project_userflow_count']['已完成']},
                {'name': '驳回', 'value': result['project_userflow_count']['驳回']}
            ];
            var data2 = [
                {'name': '已完成', 'value': result['database_release_count']['已完成']},
                {'name': '驳回', 'value': result['database_release_count']['驳回']}
            ];
            var data3 = [
                {'name': '已完成', 'value': result['database_release_count']['已完成']},
                {'name': '驳回', 'value': result['database_release_count']['驳回']}
            ];
            var data4 = [
                {'name': '已完成', 'value': result['cronflow_count']['已完成']},
                {'name': '驳回', 'value': result['cronflow_count']['驳回']}
            ];
            pie_workflow_status_fun(data1, data2, data3, data4);
        },
        complete: function() {
            $('#workflow_project_source_loading_id').hide();
            $('#workflow_exec_status_loading_id').hide();
        }
    });
}
// 项目成员的数据
function get_project_user_amount(project_id){
    $('#workflow_project_user_loading_id').show();
    $.ajax({
        url: '/flow/get_project_user_amount',
        type: 'get',
        data: {'project_id': project_id},
        success: function(result) {
            pie_workflow_project_user_fun(result);
        },
        complete: function() {
            $('#workflow_project_user_loading_id').hide();
        }
    });
}

// 工作流总数折线图
function get_flow_count(start,end) {
  var flow_amount_line = echarts.init(document.getElementById('flow_amount_line'), 'macarons');
  $('#workflow_by_type_line_loading').show();
  $.ajax({
      type: "post",
      url: "/get_flow_amount/",
      dataType: "json",
      data: {'startdate':start,'enddate':end},
      success: function(result) {
          var flow_date = [];
          var flow_count_data = [];
          var line_project_flow_count = [];
          var line_project_userflow_count = [];
          var line_cronflow_count = [];
          var line_project_releaseflow_count = [];
          var line_database_release_count = [];
          flow_date.push(result.date_list);
          flow_count_data.push(result.flow_count);
          line_project_flow_count.push(result.line_project_flow_count);
          line_project_userflow_count.push(result.line_project_userflow_count);
          line_cronflow_count.push(result.line_cronflow_count);
          line_project_releaseflow_count.push(result.line_project_releaseflow_count);
          line_database_release_count.push(result.line_database_release_count);
          $("#through_flow").html("( "+ result.through_count +" )");
          $("#no_approval_flow").html("( "+ result.no_approval_count +" )");
          $("#no_through_flow").html("( "+ result.no_through_count +" )");
          // $('#through_flow_count_id').attr('data-transitiongoal', percent).progressbar({ display_text: 'fill' });
          var through_flow_count = Math.round(result.through_count/result.all_count*100);
          if (!through_flow_count){
            through_flow_count = 0
          }
          var no_approval_flow_count = Math.round(result.no_approval_count/result.all_count*100);
          if (!no_approval_flow_count){
            no_approval_flow_count = 0
          }
          var no_through_flow_count = Math.round(result.no_through_count/result.all_count*100);
          if (!no_through_flow_count){
            no_through_flow_count = 0
          }
          $('#through_flow_count_id').attr('data-transitiongoal', through_flow_count).progressbar();
          $('#no_approval_flow_count_id').attr('data-transitiongoal', no_approval_flow_count).progressbar();
          $('#no_through_flow_count_id').attr('data-transitiongoal', no_through_flow_count).progressbar();
          flow_amount_line_option = {
          tooltip : {
              trigger: 'axis',
              position:function(p){   //其中p为当前鼠标的位置
                  return [p[0] + 10, p[1] - 10];
              }
          },
          legend: {
              data:['立项申请', '项目变更', '数据库变更', '项目成员变更', '计划任务变更']
          },
          xAxis: {
              type: 'category',
              data: eval(flow_date[0]),
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
                  name: '立项申请',
                  data: eval(line_project_flow_count[0]),
                  type: 'line',
                  smooth: true,
                  itemStyle: { normal: {label : {show: true}}}
              },
              {
                  name: '项目变更',
                  data: eval(line_project_releaseflow_count[0]),
                  type: 'line',
                  smooth: true,
                  itemStyle: { normal: {label : {show: true}}}
              },
              {
                  name: '数据库变更',
                  data: eval(line_database_release_count[0]),
                  type: 'line',
                  smooth: true,
                  itemStyle: { normal: {label : {show: true}}}
              },
              {
                  name: '项目成员变更',
                  data: eval(line_project_userflow_count[0]),
                  type: 'line',
                  smooth: true,
                  itemStyle: { normal: {label : {show: true}}}
              },
              {
                  name: '计划任务变更',
                  data: eval(line_cronflow_count[0]),
                  type: 'line',
                  smooth: true,
                  itemStyle: { normal: {label : {show: true}}}
              }
          ]
      };
      flow_amount_line.setOption(flow_amount_line_option);
      $('#workflow_by_type_line_loading').hide();
      }
  });
  window.addEventListener("resize",function(){
      flow_amount_line.resize();
  });
}

// 项目饼图
function pie_workflow_project_fun(data) {
    var pie_workflow_project = echarts.init(document.getElementById('pie_workflow_project'), 'roma');
    var pie_workflow_project_option = {
        title : {
            text: '项目来源',
            x:'center'
        },
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: ['自建项目', '外购项目']
        },
        series : [
            {
                name: '项目来源',
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
    pie_workflow_project.setOption(pie_workflow_project_option);
    window.addEventListener("resize",function(){
        pie_workflow_project.resize();
    });
}
// 项目成员饼图
function pie_workflow_project_user_fun(data) {
    var pie_workflow_project_user = echarts.init(document.getElementById('pie_workflow_project_user'), 'roma');
    var pie_workflow_project_user_option = {
        title : {
            text: '项目成员统计',
            x:'center'
        },
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: data['name_list']
        },
        series : [
            {
                name: '项目来源',
                type: 'pie',
                radius : '55%',
                center: ['50%', '60%'],
                data: data['data'],
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
    pie_workflow_project_user.setOption(pie_workflow_project_user_option);
    window.addEventListener("resize",function(){
        pie_workflow_project_user.resize();
    });
}

//执行状态饼图
function pie_workflow_status_fun(data1, data2, data3, data4) {
    var option_tem = {
        title : {
            text: '',
            x:'center'
        },
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: ['已完成', '驳回'],
            show: false
        },
        series : [
            {
                name: '项目成员统计',
                type: 'pie',
                radius : '55%',
                center: ['50%', '60%'],
                data: [],
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
    var pie_workflow_status_1 = echarts.init(document.getElementById('pie_workflow_status_1'), 'roma');
    var pie_workflow_status_2 = echarts.init(document.getElementById('pie_workflow_status_2'), 'roma');
    var pie_workflow_status_3 = echarts.init(document.getElementById('pie_workflow_status_3'), 'roma');
    var pie_workflow_status_4 = echarts.init(document.getElementById('pie_workflow_status_4'), 'roma');
    var pie_workflow_status_1_option = JSON.parse(JSON.stringify(option_tem));
    pie_workflow_status_1_option.title.text = '项目成员变更';
    pie_workflow_status_1_option.series[0].data = data1;
    var pie_workflow_status_2_option = JSON.parse(JSON.stringify(option_tem));
    pie_workflow_status_2_option.title.text = '项目变更';
    pie_workflow_status_2_option.series[0].data = data2;
    var pie_workflow_status_3_option = JSON.parse(JSON.stringify(option_tem));
    pie_workflow_status_3_option.title.text = '数据库变更';
    pie_workflow_status_3_option.series[0].data = data3;
    var pie_workflow_status_4_option = JSON.parse(JSON.stringify(option_tem));
    pie_workflow_status_4_option.title.text = '计划任务变更';
    pie_workflow_status_4_option.series[0].data = data4;
    pie_workflow_status_1.setOption(pie_workflow_status_1_option, true);
    pie_workflow_status_2.setOption(pie_workflow_status_2_option, true);
    pie_workflow_status_3.setOption(pie_workflow_status_3_option, true);
    pie_workflow_status_4.setOption(pie_workflow_status_4_option, true);
    window.addEventListener("resize",function(){
        pie_workflow_status_1.resize();
        pie_workflow_status_2.resize();
        pie_workflow_status_3.resize();
        pie_workflow_status_4.resize();
    });
}

// //点击此标签触发加载
// $("#top_dashboard div.ivu-tabs-tab:nth-child(3)").click(function(){
//   $('#top_dashboard .dashboard_tab').hide();
//   $('#dashboard_workflow_tab').show();
//   get_flow_count(moment().subtract(6,'days').startOf('day').format('YYYY-MM-DD'),moment().format('YYYY-MM-DD'));
//   get_all_workflow_amount();
// });
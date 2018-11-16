/**
 * Created by User on 2018/8/10.
 */
var cost_pillar_option_tem = {
    tooltip : {
        trigger: 'axis',
        axisPointer : {            // 坐标轴指示器，坐标轴触发有效
            type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
        },
        formatter: "{b} <br/>{c} (元)"
    },
    legend: {
        data: []
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '1%',
        containLabel: true
    },
    xAxis:  {
        type: 'value'
    },
    yAxis: {
        type: 'category',
        data: [],
    },
    series: [
        {
            name: '',
            type: 'bar',
            stack: '总量',
            label: {
                normal: {
                    show: true,
                    position: 'right',
                    formatter: "{c}元"
                }
            },
            data: []
        }
    ]
};
var cost_pie_option_tem = {
    title : {
        text: '',
        x:'center'
    },
    tooltip : {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c}元 ({d}%)"
    },
    legend: {
        orient: 'vertical',
        left: 'left',
        data: [],
        show: false
    },
    series : [
        {
            name: '',
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
                    formatter: '{b|{b}：}{c}元  {per|{d}%}\n  ',
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
function cost_amount_by_department_fun(start, end, number=10) {
    $('#by_department_amount_loading_id').show();
    var cost_pillar_by_department_amount = echarts.init(document.getElementById('cost_pillar_by_department_amount'), 'roma');
    var cost_pie_by_department_amount = echarts.init(document.getElementById('cost_pie_by_department_amount'), 'roma');
    var pillar_option = JSON.parse(JSON.stringify(cost_pillar_option_tem));
    var pie_option = JSON.parse(JSON.stringify(cost_pie_option_tem));
    $.ajax({
        url: '/costcenter/amount_by_department',
        data: {"start_date": start, "end_date": end, "number": number},
        type: 'get',
        success: function(result){
            if(result.name_list.length > 20){
                $('#cost_pillar_by_department_amount').prop("style", "height: "+result.name_list.length*20+"px");
                $('#cost_pie_by_department_amount').prop("style", "height: "+result.name_list.length*20+"px");
                cost_pillar_by_department_amount.resize();
                cost_pie_by_department_amount.resize();
            } else {
                $('#cost_pillar_by_department_amount').prop("style", "height: 400px");
                $('#cost_pie_by_department_amount').prop("style", "height: 400px");
                cost_pillar_by_department_amount.resize();
                cost_pie_by_department_amount.resize();
            }
            pillar_option.legend.data = ['部门占比'];
            pillar_option.yAxis.data = result.name_list;
            pillar_option.series[0].data = result.data_list;
            cost_pillar_by_department_amount.setOption(pillar_option);
            pie_option.series[0].name = '部门占比';
            pie_option.legend.data = result.name_list;
            pie_option.series[0].data = result.data_list;
            cost_pie_by_department_amount.setOption(pie_option);
        },
        complete: function () {
            $('#by_department_amount_loading_id').hide();
        }
    });
    window.addEventListener("resize",function(){
        cost_pillar_by_department_amount.resize();
        cost_pie_by_department_amount.resize();
    });
}

function cost_amount_by_type_fun(start, end) {
    $('#by_type_amount_loading_id').show();
    var cost_pillar_by_type_amount = echarts.init(document.getElementById('cost_pillar_by_type_amount'), 'roma');
    var cost_pie_by_type_amount = echarts.init(document.getElementById('cost_pie_by_type_amount'), 'roma');
    var pillar_option = JSON.parse(JSON.stringify(cost_pillar_option_tem));
    var pie_option = JSON.parse(JSON.stringify(cost_pie_option_tem));
    $.ajax({
        url: '/costcenter/amount_by_type',
        data: {"start_date": start, "end_date": end},
        type: 'get',
        success: function(result){
            pillar_option.legend.data = ['物品类型占比'];
            pillar_option.yAxis.data = result.name_list;
            pillar_option.series[0].data = result.data_list;
            cost_pillar_by_type_amount.setOption(pillar_option);
            pie_option.series[0].name = '物品类型占比';
            pie_option.legend.data = result.name_list;
            pie_option.series[0].data = result.data_list;
            cost_pie_by_type_amount.setOption(pie_option);
        },
        complete: function () {
            $('#by_type_amount_loading_id').hide();
        }
    });
    window.addEventListener("resize",function(){
        cost_pillar_by_type_amount.resize();
        cost_pie_by_type_amount.resize();
    });
}

function cost_amount_by_purchase_type_fun(start, end) {
    $('#by_purchase_type_amount_loading_id').show();
    var cost_pillar_by_purchase_type_amount = echarts.init(document.getElementById('cost_pillar_by_purchase_type_amount'), 'roma');
    var cost_pie_by_purchase_type_amount = echarts.init(document.getElementById('cost_pie_by_purchase_type_amount'), 'roma');
    var pillar_option = JSON.parse(JSON.stringify(cost_pillar_option_tem));
    var pie_option = JSON.parse(JSON.stringify(cost_pie_option_tem));
    $.ajax({
        url: '/costcenter/amount_by_purchase_type',
        data: {"start_date": start, "end_date": end},
        type: 'get',
        success: function(result){
            pillar_option.legend.data = ['购买类型占比'];
            pillar_option.yAxis.data = result.name_list;
            pillar_option.series[0].data = result.data_list;
            cost_pillar_by_purchase_type_amount.setOption(pillar_option);
            pie_option.series[0].name = '购买类型占比';
            pie_option.legend.data = result.name_list;
            pie_option.series[0].data = result.data_list;
            cost_pie_by_purchase_type_amount.setOption(pie_option);
        },
        complete: function () {
            $('#by_purchase_type_amount_loading_id').hide();
        }
    });
    window.addEventListener("resize",function(){
        cost_pillar_by_purchase_type_amount.resize();
        cost_pie_by_purchase_type_amount.resize();
    });
}

// $("#top_dashboard div.ivu-tabs-tab:nth-child(9)").click(function(){
//   $('#top_dashboard .dashboard_tab').hide();
//   $('#dashboard_cost_tab').show();
//   $('#cost_amount_range span').html('选择时间范围');
//   cost_amount_by_department_fun('', '');
//   cost_amount_by_type_fun('', '');
//   cost_amount_by_purchase_type_fun('', '');
//   $('#cost_amount_range').daterangepicker({
//       // startDate: moment().subtract(6,'days').startOf('day'),
//       // endDate: moment(),
//       minDate: '01/01/2017',    //最小时间
//       maxDate : moment(), //最大时间
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
//       $('#cost_amount_range span').html(start.format('YYYY-MM-DD') + ' ~ ' + end.format('YYYY-MM-DD'));
//       cost_amount_by_department_fun(start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'));
//       cost_amount_by_type_fun(start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'));
//       cost_amount_by_purchase_type_fun(start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'));
//   });
// });

// function cost_look_all_action(status) {
//     if ($('#cost_amount_range input').val() === '选择时间范围'){
//         var start = '';
//         var end = '';
//     } else {
//         var date_range = $('#cost_amount_range span').html().split(' ~ ');
//         var start = date_range[0];
//         var end = date_range[1];
//     }
//     if (status) {
//         var number = '';
//         $('#cost_look_all_action').hide();
//         $('#cost_look_section_action').show();
//     } else {
//         var number = 10;
//         $('#cost_look_section_action').hide();
//         $('#cost_look_all_action').show();
//     }
//     cost_amount_by_department_fun(start, end, number);
// }

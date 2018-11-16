/**
 * Created by User on 2018/8/11.
 */
function detectionData(air) {
    var color = new echarts.graphic.LinearGradient(0, 0, 1, 1,
    [{
        offset: 0,
        color: '#ffc000'
    }, {
        offset:1,
        color: '#0aca3f'
    }]);
    var level = '正常';
    if (air > 70 && air <= 80) {
        color = new echarts.graphic.LinearGradient(0, 0, 1, 1,
        [{
            offset: 0,
            color: '#ed4500'
        }, {
            offset:1,
            color: '#ff8a00'
        }]);
        level = '偏高';

    } else if (air > 80 && air <= 90) {
        color = new echarts.graphic.LinearGradient(0, 0, 1, 1,
        [{
            offset: 0,
            color: '#a70213'
        }, {
            offset:1,
            color: '#be19cb'
        }]);
        level = '警告';
    } else if (air > 90) {
        color = new echarts.graphic.LinearGradient(0, 0, 1, 1,
        [{
            offset: 0,
            color: '#a70213'
        }, {
            offset:1,
            color: '#a70213'
        }]);
        level = '严重';
    }
    return {
        color: color,
        level: level
    };
};

var system_run_gauge_option = {
    series: [
        {
            name: '业务',
            type: 'gauge',
            radius: '100%',
            animationDuration: 6000,
            animationThreshold: 8000,
            animationDelay: 10,
            startAngle: 245,
            endAngle: -65,
            axisLine: {
                show: true,
                lineStyle: {
                    width: 15,
                    color: [[0, '#eee'], [1, '#eee']],
                }
            },
            splitLine: {show: false},
            axisTick: {show: false},
            axisLabel: {show: false},
            splitLabel: {show: false},
            pointer: {show: false},
            itemStyle: {
                borderWidth: 30,
                color: '#000',
            },
            title: {
                offsetCenter: [0, '-20%'],
                color: 'rgba(0, 0, 0, 0.6)',
                fontSize: 13,
            },
            detail: {
                formatter:'{value}',
                color: 'rgba(0, 0, 0, 0.6)',
                offsetCenter: [0, '25%'],
                lineHeight: 26
            },
            data: []
        }
    ],
};

var system_run_pie_option = {
    title : {
        text: '',
        x:'center'
    },
    tooltip : {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c}GB ({d}%)"
    },
    legend: {
        orient: 'vertical',
        left: 'left',
        data: ['已用', '空闲'],
        show: false
    },
    series : [
        {
            name: '磁盘使用率',
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
                    formatter: '{b|{b}：}{c}GB  {per|{d}%}\n  ',
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


function gauge_cpu_fun(data) {
    $('#system_gauge_cpu_loading_id').show();
    var gauge_picture = echarts.init(document.getElementById('system_gauge_cpu'), 'roma');
    var system_run_cpu_usage_option = JSON.parse(JSON.stringify(system_run_gauge_option));
    var {color, level} = detectionData(data);
    // system_run_cpu_usage_option.title.text = 'cpu使用率';
    system_run_cpu_usage_option.series[0].axisLine.lineStyle.color[0][0] = data/100;
    system_run_cpu_usage_option.series[0].axisLine.lineStyle.color[0][1] = color;
    system_run_cpu_usage_option.series[0].data = [{name: 'CPU使用率\n\n'+level, value: data}];
    gauge_picture.setOption(system_run_cpu_usage_option);
    window.addEventListener("resize",function(){
        gauge_picture.resize();
    });
    $('#system_gauge_cpu_loading_id').hide();
}

function gauge_memory_fun(data) {
    $('#system_gauge_mem_loading_id').show();
    var gauge_picture = echarts.init(document.getElementById('system_gauge_mem'), 'roma');
    var system_run_memory_usage_option = JSON.parse(JSON.stringify(system_run_gauge_option));
    var {color, level} = detectionData(data);
    // system_run_memory_usage_option.title.text = '内存使用率';
    system_run_memory_usage_option.series[0].axisLine.lineStyle.color[0][0] = data/100;
    system_run_memory_usage_option.series[0].axisLine.lineStyle.color[0][1] = color;
    system_run_memory_usage_option.series[0].data = [{name: '内存使用率\n\n'+level, value: data}];
    gauge_picture.setOption(system_run_memory_usage_option);
    window.addEventListener("resize",function(){
        gauge_picture.resize();
    });
    $('#system_gauge_mem_loading_id').hide();
}

function gauge_disk_fun(disk_partition) {
    $('#system_gauge_disk_loading_id').show();
    $('#system_gauge_disk').html('');
    var partition_id = 0;
    var part_div_id;
    var width = '100%';
    var len = 0;
    for (var v in disk_partition) {
        len += 1;
    }
    if (len > 1){
        width = '415px';
    }
    for (var i in disk_partition){
        partition_id += 1;
        var used = (disk_partition[i]['used'] / 1024 / 1024 / 1024).toFixed(0);
        var idle = ((disk_partition[i]['total'] - disk_partition[i]['used']) / 1024 / 1024 / 1024).toFixed(0);
        if (used === '0' && idle === '0'){
            continue
        }
        part_div_id = "system_gauge_disk_partition_"+partition_id;
        $('#system_gauge_disk').append('<div id="'+part_div_id+'" style="width: '+width+';height: 190px;display:inline-block"></div>');
        var pie_picture = echarts.init(document.getElementById(part_div_id), 'roma');
        var pie_option = JSON.parse(JSON.stringify(system_run_pie_option));
        pie_option.title.text = i;
        pie_option.series[0].data = [{'name': '已用', 'value': used}, {'name': '空闲', 'value': idle}];
        pie_picture.setOption(pie_option);
        window.addEventListener("resize",function(){
            pie_picture.resize();
        });
    }
    $('#system_gauge_disk_loading_id').hide();
}

function system_run_get_laod_fun(one_minute_load, five_minute_load, fifteen_minute_load) {
    $('#system_gauge_load_line_loading_id').show();
    var load_line = echarts.init(document.getElementById('system_gauge_load'), 'roma');
    var load_line_option = {
        title: {
            show: "true",//是否显示标题，默认显示，可以不设置
            text: "平均负载",//图表标题文本内容
            textStyle:{//标题内容的样式
                color:'#333333',
                fontWeight:"lighter",//可选normal(正常)，bold(加粗)，bolder(加粗)，lighter(变细)，100|200|300|400|500...
                fontSize:14 //主题文字字体大小，默认为18px
            }
        },
        toolbox: {
            show: true,
            feature: {
                dataZoom: {
                    yAxisIndex: 'none'
                },
                dataView: {readOnly: false},
                magicType: {type: ['line', 'bar']},
                restore: {},
                saveAsImage: {}
            }
        },
        tooltip : {
            trigger: 'axis',
            position:function(p){   //其中p为当前鼠标的位置
                return [p[0] + 10, p[1] - 10];
            },
            formatter: function (params, ticket, callback) {
                var params_date = params[0]['data'][0];
                var params_value = params[0]['data'][1];
                var params_date_1 = params[1]['data'][0];
                var params_value_1 = params[1]['data'][1];
                var params_date_2 = params[2]['data'][0];
                var params_value_2 = params[2]['data'][1];
                return "时间："+params_date+"<br>一分钟平均负载："+params_value+"<br>五分钟平均负载："+params_value_1+"<br>十五分钟平均负载："+params_value_2+"<br>";
            }
        },
        legend: {
            show:true
        },
        xAxis: {
            type: 'time',
            axisLine:{
                lineStyle:{
                    color:'#333333'
                }
            },
            splitLine:{
        　　　　show:true
        　　}
        },
        yAxis: {
            type: 'value',
            axisLine:{
                lineStyle:{
                    color:'#333333'
                }
            },
            splitLine:{
        　　　　show:true
        　　}
        },
        series: [
          {
            name: '一分钟平均负载',
            data: eval(one_minute_load),
            type: 'line',
            smooth: true,
            showSymbol:false,
            lineStyle: {
                normal: {
                    width: 1
                }
            }
          },
          {
            name: '五分钟平均负载',
            data: eval(five_minute_load),
            type: 'line',
            smooth: true,
            showSymbol:false,
            lineStyle: {
                normal: {
                    width: 1
                }
            }
          },
          {
            name: '十五分钟平均负载',
            data: eval(fifteen_minute_load),
            type: 'line',
            smooth: true,
            showSymbol:false,
            lineStyle: {
                normal: {
                    width: 1
                }
            }
          }
        ]
    };
    load_line.setOption(load_line_option);
    window.addEventListener("resize",function(){
        load_line.resize();
    });
    $('#system_gauge_load_line_loading_id').hide();
}

function system_run_get_memory_line_fun(data) {
    $('#system_gauge_memory_line_loading_id').show();
    var memory_line = echarts.init(document.getElementById('system_gauge_memory'), 'roma');
    var memory_usage_line_option = {
        title: {
            show: "true",//是否显示标题，默认显示，可以不设置
            text: "内存",//图表标题文本内容
            textStyle:{//标题内容的样式
                color:'#333333',
                fontWeight:"lighter",//可选normal(正常)，bold(加粗)，bolder(加粗)，lighter(变细)，100|200|300|400|500...
                fontSize:14 //主题文字字体大小，默认为18px
            }
        },
        toolbox: {
            show: true,
            feature: {
                dataZoom: {
                    yAxisIndex: 'none'
                },
                dataView: {readOnly: false},
                magicType: {type: ['line', 'bar']},
                restore: {},
                saveAsImage: {}
            }
        },
        tooltip : {
            trigger: 'axis',
            position:function(p){   //其中p为当前鼠标的位置
                return [p[0] + 10, p[1] - 10];
            },
            formatter: function (params, ticket, callback) {
                var params_date = params[0]['data'][0];
                var params_value = params[0]['data'][1];
                return "时间："+params_date.replace('T', ' ')+"<br>内存使用率："+params_value+"(%)";
            }
        },
        legend: {
            show:true
        },
        xAxis: {
            type: 'time',
            axisLine:{
                lineStyle:{
                    color:'#333333'
                }
            },
            splitLine:{
        　　　　show:true
        　　}
        },
        yAxis: {
            min:0,
            max:100,
            type: 'value',
            axisLine:{
                lineStyle:{
                    color:'#333333'
                }
            },
            splitLine:{
        　　　　show:true
        　　}
        },
        series: [{
            name: '内存使用率(%)',
            data: eval(data),
            type: 'line',
            smooth: true,
            areaStyle: {},
            showSymbol: false,
            lineStyle: {
                normal: {
                    width: 1
                }
            }
        }]
    };
    memory_line.setOption(memory_usage_line_option);
    window.addEventListener("resize",function(){
        memory_line.resize();
    });
    $('#system_gauge_memory_line_loading_id').hide();
}

// 获取实例的资源水位
function system_run_get_server_amount(server_id){
    $.ajax({
        url: '/opscenter/server/dashboard_server_monitor',
        type: 'get',
        data: {'server_id': server_id},
        success: function(result) {
            if (result){
                if (result.now_time){
                    $('#system_run_data_time').html((result.now_time).replace('T', ' '));
                }
                gauge_cpu_fun(result.cpu_usage);
                gauge_memory_fun(result.memory_usage);
                gauge_disk_fun(result.disk_partition);
                if (result['memory_percent'].length > 0){
                    system_run_get_memory_line_fun(result['memory_percent']);
                }
                if (result['one_minute_load'].length > 0 || result['five_minute_load'].length > 0 || result['fifteen_minute_load'].length > 0){
                    // $('#system_run_load').show();
                    system_run_get_laod_fun(result['one_minute_load'], result['five_minute_load'], result['fifteen_minute_load']);
                } else {
                    // $('#system_run_load').hide();
                    $('#system_gauge_load').html('');
                    $('#system_gauge_load').removeAttr('_echarts_instance_');
                }
            }
        }
    });
}

function get_web_detect(){
    $("#web_detect_loading_id").show();
    $('#web_detect').html('');
    $.ajax({
        url: '/opscenter/get_web_detect',
        type: 'get',
        success: function(result) {
            var tag_count = 0;
            var panel = '';
            for (var i in result.result){
                tag_count += 1;
                var color;
                if ((result.result[i]["code"]+'')[0] === '2'){
                    color = 'green';
                } else if ((result.result[i]["code"]+'')[0] === '3'){
                    color = 'yellow';
                } else {
                    color = 'red';
                }
                var my_c = '<span style="text-align: left; margin-left:10px">'+result.result[i]["description"]+'( '+result.result[i]["name"]+' )</span>' +
                            '<tag color="'+color+'" style="margin-left:15px;">'+result.result[i]["code"]+'</tag>' +
                            '<span style="float:right; color:red; margin-right:10px">'+result.result[i]["time"]+'</span>'+
                            '<pre slot="content" style="font-size:14px;padding:0;background-color:#fff;border:none;height: 100%">'+result.result[i]["content"]+'</pre>';
                panel += '<panel name="'+tag_count+'">'+my_c+'</panel>';

            }
            $('#web_detect').append(
                '<collapse v-model="value1">'+panel+'</collapse>'
            );
            var Main = {
                data () {
                    return {
                        value1: '1'
                    };
                }
            };
            var Component = Vue.extend(Main);
            new Component().$mount('#web_detect');
        },
        complete: function(){
            $("#web_detect_loading_id").hide();
        }
    });
}
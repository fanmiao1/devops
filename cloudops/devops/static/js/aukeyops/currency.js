/**
 * Created by User on 2018/5/31.
 */

$.getScript('/static/js/message.js');

//bootstrapTable获取选择的行
function getSelectRow() {
   var getSelectRows = $("#table").bootstrapTable('getSelections', function (row) {
        return row;
    });
   for (i in getSelectRows){
       var row_result = getSelectRows[i]
   }
   return row_result;
}

//Json对象转化Dict
function jsonToDict(json_obj) {
    var form_dict = {};
    for (i in json_obj) {
        form_dict[json_obj[i]['name']] = json_obj[i]['value']
    }
    return form_dict
}

// 时间戳转化为日期/时间，当type为'date'时，返回yyyy-mm-dd格式,否则返回yyyy-mm-dd hh:MM:ss
function timestampToTime(timestamp, type) {
    var date = new Date(timestamp * 1000);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
    var Y = date.getFullYear() + '-';
    var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
    var D = date.getDate();
    var h = date.getHours() + ':';
    var m = date.getMinutes() + ':';
    var s = date.getSeconds();
    if (type == 'date') {
        return Y+M+D;
    } else {
        return Y+M+D+' '+h+m+s;
    }
}

// 获取当前日期/时间，当type为'date'时，返回yyyy-mm-dd格式,否则返回yyyy-mm-dd hh:MM:ss
function getNowTime(type) {
    var date = new Date();
    var year = date.getFullYear();
    var month = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1);
    var day = date.getDate();
    var hour = date.getHours() + ':';
    var minute = date.getMinutes() + ':';
    var second = date.getSeconds();
    if (type == 'date'){
        var nowTime = year+"-"+month+"-"+day;
    } else {
        var nowTime = year+"-"+month+"-"+day+" "+hour+minute+second;
    }
    return nowTime
}

// 计算天数差，当sDate2为'now'时，计算距离当前日期的天数
function daysBetween(sDate1, sDate2) {
    //Date.parse() 解析一个日期时间字符串，并返回1970/1/1 午夜距离该日期时间的毫秒数
    var time1 = Date.parse(new Date(sDate1));
    if (sDate2 === 'now') {
        var time2 = Date.parse(new Date(getNowTime('date')));
    } else {
        var time2 = Date.parse(new Date(sDate2));
    }
    var nDays = Math.abs(parseInt((time1 - time2)/1000/3600/24));
    if (time1 > time2){
        return nDays;
    } else {
        return -nDays;
    }
}

// 计算分钟差，当sDate2为'now'时，计算距离当前时间的分钟数
function minutesBetween(sDate1, sDate2) {
    var time1 = Date.parse(new Date(sDate1));
    if (sDate2 === 'now') {
        var time2 = Date.parse(getNowTime('time'));
    } else {
        var time2 = Date.parse(new Date(sDate2));
    }
    var nMinutes = Math.abs(parseInt((time2 - time1)/1000/60));
    return  nMinutes;
}


// 检查必填
function checkRequired(FormId) {
    var required_input = $('#'+FormId).find("[class*='is_required']");
    var have_not_write = 0;
    for (var i=0;i < required_input.length; i++) {
        if (!required_input[i].value) {
            have_not_write = 1;
            $(required_input[i]).addClass('error_input');
            $(required_input[i]).after("<div class='error_alert'>此项不能为空。</div>");
        }
    }
    if (have_not_write === 1) {
        return false
    } else {
        return true
    }
}

function checkInt(FormId) {
    var int_input = $('#'+FormId).find("[class*='is_int']");
    var have_not_write = 0;
    for (var i=0;i < int_input.length; i++) {
        if (int_input[i].value){
            if (!parseInt(int_input[i].value) || !parseFloat(int_input[i].value)) {
                have_not_write = 1;
                $(int_input[i]).addClass('error_input');
                $(int_input[i]).after("<div class='error_alert'>请输入正确的类型。</div>");
            }
        }
    }
    if (have_not_write == 1) {
        return false
    } else {
        return true
    }
}

// 清除错误提示
function cleanErrorAlert(FormId) {
    $('.error_alert').remove();
    $("#"+FormId).find("[class*='error_input']").removeClass("error_input");
}

// 添加或修改
function change_request (url, type) {
    $.ajax({
        url: url,
        data: $('#change_form').serializeArray(),
        datatype: 'json',
        type: type,
        success: function (result) {
            MyMessage(1, '操作成功！');
            $('#changing_loading_id').hide();
            $('#changeModal').modal('hide');
            $('#table').bootstrapTable("refresh");
        },
        error: function (result) {
            MyMessage(0, result.responseText);
            var re_json = result.responseJSON;
            for (i in re_json){
                $("#change_form [name="+i+"]").addClass('error_input');
                $("#change_form [name="+i+"]").after("<div class='error_alert'>"+result.responseJSON[i]+"</div>")
            }
            $('#changing_loading_id').hide();
        }
    })
}

// Json格式化
function JsonFormat(json) {  
    if (typeof json != 'string') {  
        json = JSON.stringify(json, undefined, 2);  
    }  
    json = json.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');  
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {  
        var cls = 'number';  
        if (/^"/.test(match)) {  
                if (/:$/.test(match)) {  
                    cls = 'key';  
                } else {  
                    cls = 'string';  
                }  
        } else if (/true|false/.test(match)) {  
            cls = 'boolean';  
        } else if (/null/.test(match)) {  
            cls = 'null';  
        }  
        return '<span class="' + cls + '">' + match + '</span>';  
    });  
}


// 获取所有用户添加到下拉选择器
function GetAllUserToSelect(SelectId) {
    $.ajax({
       url: "/get_all_user/",
       type: "get",
       success: function(result){
        console.log(result)
           $('#'+SelectId+'.selectpicker').append('<option></option>');
           $.each(result.result, function (index, item) {
               $('#'+SelectId+'.selectpicker').append('<option value=' + item['value'] + '>' + item['name'] + '</option>');
           });
           $('#'+SelectId+'.selectpicker').selectpicker('refresh');
       }
    });
}

// 刷新表格
function refresh_table(TableId='table') {
    $('#'+TableId).bootstrapTable("refresh");
}
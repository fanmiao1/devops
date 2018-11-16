/**
 * Created by User on 2018/8/7.
 * 待办
 */
var server_and_domain_expired_at_once = 0;
function get_wait_process_message() {
    $.ajax({
        type: "post",
        url: "/get_wait_process_message/",
        success: function(result) {
            if (result['code'] == 0){
                document.getElementById("unread_impo_row_id").style.display= "none";
            }else {
                if (result.result.length == 0){
                    var aText = '<div style="height:100%;width:100%;text-align:center;padding-top:20%"><span style="font-size:25px;color:#999;opacity:0.3;-webkit-user-select:none;user-select:none;">暂无待办</span></div>';
                    document.getElementById("unread_impo").innerHTML = aText;
                    $('#unread_impo_loading_id').hide();
                }else {
                    $('#upcoming_workflow_wait_process').html(result.result.length);
                    $.each(result.result, function (index, item) {
                        if (item['type'] == '审批') {
                            var the_color = '#D9534F';
                        } else {
                            var the_color = '#5B2C6F';
                        }
                        var aText = '<li><a href="' + item['url'] + '" style="display:block;">' + item['title'] + '<span class"label label-danger" style="float:right;color:' + the_color + ';padding-right: 5px;">' + item['type'] + '</span></a></li>';
                        var ahtml = document.getElementById("unread_impo_todo_id").innerHTML;
                        document.getElementById("unread_impo_todo_id").innerHTML = ahtml + aText;
                        $('#unread_impo_loading_id').hide();
                    });
                }
                if (result.result2.length == 0){
                    var bText = '<div style="height:100%;width:100%;text-align:center;padding-top:20%"><span style="font-size:25px;color:#999;opacity:0.3;-webkit-user-select:none;user-select:none;">暂无申请记录</span></div>';
                    document.getElementById("my_app_record_divid").innerHTML = bText;
                    $('#my_app_record_divid_loading_id').hide();
                }else {
                    $.each(result.result2, function (index, item) {
                        var bText = '<li><a href="' + item['url'] + '" style="display:block;">' + item['title'] + '<span class"label label-danger" style="float:right;padding-right: 5px;">' + item['type'] + '</span></a></li>';
                        var bhtml = document.getElementById("my_app_record_ulid").innerHTML;
                        document.getElementById("my_app_record_ulid").innerHTML = bhtml + bText;
                        $('#my_app_record_divid_loading_id').hide();
                    });
                }
                if (result.result3.length == 0){
                    var cText = '<div style="height:100%;width:100%;text-align:center;padding-top:20%"><span style="font-size:25px;color:#999;opacity:0.3;-webkit-user-select:none;user-select:none;">暂无需要处理的工单</span></div>';
                    document.getElementById("my_pro_worksheet_divid").innerHTML = cText;
                    $('#my_pro_worksheet_divid_loading_id').hide();
                }else {
                    $('#upcoming_worksheet_wait_process').html(result.result3.length);
                    $.each(result.result3, function (index, item) {
                        var cText = '<li><a href="' + item['url'] + '" style="display:block;"><span style="padding-right: 5px;">' + item['title'] + '</span></a></li>';
                        var chtml = document.getElementById("my_pro_worksheet_ulid").innerHTML;
                        document.getElementById("my_pro_worksheet_ulid").innerHTML = chtml + cText;
                        $('#my_pro_worksheet_divid_loading_id').hide();
                    });
                }
            }
        }
    });
}

function get_server_count_amount(){
    $.ajax({
        url: '/opscenter/server/get_amount',
        type: 'get',
        success: function(result) {
            $('#upcoming_server_total').html(result['total']);
            $('#upcoming_server_run').html(result['run']);
            $('#upcoming_server_expired_at_once').html(result['expired_at_once']);
            $('#upcoming_server_expired').html(result['expired']);
            server_and_domain_expired_at_once += result['expired_at_once'];
            $('#server_and_domain_expired_at_once').html(server_and_domain_expired_at_once);
        }
    });
}
function get_domain_count_amount(){
    $.ajax({
        url: '/cmdb/domain/get_amount',
        type: 'get',
        success: function(result) {
            $('#upcoming_domain_total').html(result['total']);
            $('#upcoming_domain_run').html(result['run']);
            $('#upcoming_domain_expired_at_once').html(result['expired_at_once']);
            $('#upcoming_domain_expired').html(result['expired']);
            server_and_domain_expired_at_once += result['expired_at_once'];
            $('#server_and_domain_expired_at_once').html(server_and_domain_expired_at_once);
        }
    });
}

$(document).ready(function(){
    get_wait_process_message();
    get_server_count_amount();
    get_domain_count_amount();
});

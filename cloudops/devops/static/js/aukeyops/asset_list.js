/**
 * Created by User on 2018/5/24.
 */
$.getScript('/static/js/message.js');
var Item = 0;
function addItem(){
    Item += 1;
    $("#add_item_group").append('\
    <div class="form-group" id="item_'+Item+'">\
        <input type="text" id="item_input_'+Item+'" style="display:none">\
        <label class="ivu-form-item-label pull-left col-md-2">\
        <input class="ivu-input" required="required" type="text" placeholder="字段名" id="item_label_'+Item+'" autocomplete="off"></label>\
        <div class="col-md-8 col-sm-8 col-xs-8" style="padding-right:0">\
        <input class="ivu-input" required="required" type="text" autocomplete="off" placeholder="值" id="item_value_'+Item+'"></div>\
        <div class="col-md-2 col-sm-2 col-xs-2" style="padding-left:0">\
        <button class="btn btn-link" type="button" onclick="delItem(\'item_'+Item+'\')" style="font-size:12px;">移除字段</button>\
        </div>\
    </div>')
}
function delItem(item){
    $("#"+item).remove();
}
function addAsset() {
    var add_asset_id = $('#add_asset_id').val().replace(/(^\s*)|(\s*$)/g, "");
    var add_asset_type_id = $('#add_asset_type_id').val().replace(/(^\s*)|(\s*$)/g, "");
    var add_status_id = $('#add_status_id').val().replace(/(^\s*)|(\s*$)/g, "");
    if (add_asset_id == ''){
        MyMessage(0, '资产编号不能为空！');
        return false;
    }else if (add_asset_type_id == ''){
        MyMessage(0, '资产类型不能为空！');
        return false;
    }else if (add_status_id == ''){
        MyMessage(0, '状态不能为空！');
        return false;
    }else{
        var child_element = $('#add_item_group').children().size();
        if (child_element > 0){
            for (i = 0; i < child_element; i++){
                var form_id = $('#add_item_group').children()[i].id;
                var input_id = $('#'+form_id+" input").attr('id');
                var input_element = $('#'+input_id);
                var label = $('#'+form_id+" label input").val();
                var value = $('#'+form_id+" div:first input").val();
                if (label == ''){
                    MyMessage(0, '字段名不能为空！');
                    return false;
                }else if (value == ''){
                    MyMessage(0, '字段「'+label+'」的值不能为空！');
                    return false;
                }
                input_element.attr("name",label);
                input_element.val(value);
            }
        }
        $('#add_submit_btn').addClass('ivu-btn-loading');
        $.ajax({
            url:"/cmdb/asset_manage/fixed_asset/add_asset/",
            type: 'post',
            data: $('#add_asset_form').serialize(),
            success: function(result) {
                MyMessage(result['code'], result['result']);
                if (result['code'] == 1){
                    $('#table').bootstrapTable("refresh");
                    Item = 0;
                    $('#myModal').modal('hide');
                }
                $('#add_submit_btn').removeClass('ivu-btn-loading');
            },
            error: function () {
                $('#add_submit_btn').removeClass('ivu-btn-loading');
            }
        });
    }
}
$(function(){
    $('#add_asset_type_id').change(function(e){
        $.ajax({
            url: "/cmdb/asset_manage/fixed_asset/get_asset_field/",
            type: "post",
            data: {'type_id': e.target.value},
            success: function(result) {
                $("#add_my_field_group").empty();
                if (result['result']){
                    var my_field_num = 0;
                    for (i in result['result']){
                        my_field_num += 1;
                        $("#add_my_field_group").append('\
                        <div class="form-group" id="my_field_'+my_field_num+'">\
                            <label class="ivu-form-item-label pull-left col-md-2">'+result['result'][i]+'</label>\
                            <div class="col-md-10 col-sm-10 col-xs-10" style="padding-right:0">\
                            <input class="ivu-input" required="required" type="text" autocomplete="off" \
                            name="'+result['result'][i]+'" id="my_field_value_'+my_field_num+'"></div>\
                        </div>')
                    }
                }
            }
        })
    })
});
//资产添加结束
// 打开资产借出
function openAssetOut() {
    var select = getSelectRow();
    if (select && select.status) {
        if (select.status != '在库') {
            MyMessage(0, '该资产目前为「' + select.status + '」状态，不能借出！');
            return false
        } else {
            $('#assetOutModal').modal('show');
            if (select.asset_id) {
                $('#asset_out_id').val(select.asset_id);
            }
        }
    }else{
        $('#assetOutModal').modal('show');
    }
}
// 资产借出动作
function ActionassetOut() {
    if ($('#asset_out_id').val() == ''){
        MyMessage(0, '资产编号不能为空！');
    }else if ($('#asset_use_person_id').val() == ''){
        MyMessage(0, '领用人不能为空！');
    }else{
        $('#asset_out_submit_btn').addClass('ivu-btn-loading');
        $.ajax({
            url:"/cmdb/asset_manage/fixed_asset/asset_out/",
            type: 'post',
            data: $('#asset_out_form').serialize(),
            success: function(result) {
                MyMessage(result['code'], result['result']);
                if (result['code'] == 1){
                    $('#assetOutModal').modal('hide');
                    $('#table').bootstrapTable("refresh");
                }
                $('#asset_out_submit_btn').removeClass('ivu-btn-loading');
            },
            error: function () {
                $('#asset_out_submit_btn').removeClass('ivu-btn-loading');
            }
        });
    }
}
function openAssetBack() {
    var select = getSelectRow();
    if (select && select.status){
        if (select.status == '在库'){
            MyMessage(0, '该资产目前为「'+select.status+'」状态，不能归还！');
            return false
        }else{
            $('#assetBackModal').modal('show');
            if (select.asset_id){
                $('#asset_back_id').val(select.asset_id);
                $.ajax({
                    url: "/cmdb/asset_manage/fixed_asset/judge_back_person/",
                    type: "post",
                    data: {"asset_id": select.asset_id},
                    success: function(result) {
                        $('#asset_back_person_id').val(result['result']);
                    }
                });
            }
        }
    }else{
        $('#assetBackModal').modal('show');
    }
}
// 资产归还动作
function ActionassetBack() {
    if ($('#asset_back_id').val() == ''){
        MyMessage(0, '资产编号不能为空!');
    }else if ($('#asset_back_person_id').val() == ''){
        MyMessage(0, '归还人不能为空！');
    }else{
        $('#asset_back_submit_btn').addClass('ivu-btn-loading');
        $.ajax({
            url: "/cmdb/asset_manage/fixed_asset/asset_back/",
            type: 'post',
            data: $('#asset_back_form').serialize(),
            success: function(result) {
                MyMessage(result['code'], result['result']);
                if (result['code'] == 1){
                    $('#assetBackModal').modal('hide');
                    $('#table').bootstrapTable("refresh");
                }
                $('#asset_back_submit_btn').removeClass('ivu-btn-loading');
            },
            error: function () {
                $('#asset_back_submit_btn').removeClass('ivu-btn-loading');
            }
        });
    }
}
// 打开资产维修
function openAssetMaintain() {
    var select = getSelectRow();
    if (select && select.status){
        if (select.status != '在库'){
            MyMessage(0, '该资产目前为「'+select.status+'」状态，不能维修！');
            return false
        }else{
            $('#assetMaintainModal').modal('show');
            if (select.asset_id){
                $('#asset_maintain_id').val(select.asset_id);
            }
        }
    }else{
        $('#assetMaintainModal').modal('show');
    }

}
// 点击供应商报修按钮
$("#supplier_ma_input_id").click(function(){
    if ($("#supplier_ma_input_id").is(":checked")){
        // 判断该资产是否绑定供应商
        if ($('#asset_maintain_id').val() == ''){
            MyMessage(0, '请先填写资产编号！');
            return false
        }else{
            $.ajax({
                url: "/cmdb/asset_manage/fixed_asset/judge_supplier/",
                type: "post",
                data: {'asset_id': $('#asset_maintain_id').val()},
                success: function(result) {
                    if (result['code'] == 1) {
                        $('#asset_maintain_person_id').val(result['result']);
                        $("#asset_maintain_person_id").attr('readOnly','false');
                    } else {
                        MyMessage(0, result['result']);
                        $("#supplier_ma_input_id").prop("checked",false);
                    }
                }
            });
        }
    }else{
        $("#asset_maintain_person_id").removeAttr('readOnly');
    }
});
// 资产维修动作
function ActionassetMaintain() {
    if ($('#asset_maintain_id').val() == ''){
        MyMessage(0, '资产编号不能为空！');
        return false;
    } else if ($('#asset_maintain_person_id').val() == ''){
        MyMessage(0, '维修方不能为空！');
        return false;
    } else {
        $('#asset_maintain_submit_btn').addClass('ivu-btn-loading');
        $.ajax({
            url:"/cmdb/asset_manage/fixed_asset/asset_maintain/",
            type: 'post',
            data: $('#asset_maintain_form').serialize(),
            success: function(result) {
                MyMessage(result['code'], result['result']);
                if (result['code'] == 1){
                    $('#assetMaintainModal').modal('hide');
                    $('#table').bootstrapTable("refresh");
                }
                $('#asset_maintain_submit_btn').removeClass('ivu-btn-loading');
            },
            error: function () {
                $('#asset_maintain_submit_btn').removeClass('ivu-btn-loading');
            }
        });
    }
}

// 打开资产报废
function openAssetScrap() {
    var select = getSelectRow();
    if (select && select.status) {
        if (select.status != '在库') {
            MyMessage(0, '该资产目前为「' + select.status + '」状态，不能报废！');
            return false
        } else {
            $('#assetScrapModal').modal('show');
            if (select.asset_id) {
                $('#asset_scrap_id').val(select.asset_id);
            }
        }
    }else{
        $('#assetScrapModal').modal('show');
    }
}
// 资产报废动作
function ActionassetScrap() {
    if ($('#asset_scrap_id').val() == ''){
        MyMessage(0, '资产编号不能为空！');
    }else{
        $("#asset_scrap_submit_btn").addClass('ivu-btn-loading');
        $.ajax({
            url:"/cmdb/asset_manage/fixed_asset/asset_scrap/",
            type: 'post',
            data: $('#asset_scrap_form').serialize(),
            success: function(result) {
                MyMessage(result['code'], result['result']);
                if (result['code'] == 1){
                    $('#assetScrapModal').modal('hide');
                    $('#table').bootstrapTable("refresh");
                }
                $("#asset_scrap_submit_btn").removeClass('ivu-btn-loading');
            },
            error: function () {
                $("#asset_scrap_submit_btn").removeClass('ivu-btn-loading');
            }
        });
    }
}

// 删除资产
function confirmDelete(){
    var select = getSelectRow();
    if (select && select.status) {
        if (select.status != '在库') {
            MyMessage(0, '该资产目前为「' + select.status + '」状态，不能删除！');
            return false;
        } else {
            if (select.asset_id) {
                $.confirm({
                    title: '提示！',
                    content: '确定要删除资产「'+select.asset_id+'」吗？',
                    closeIcon: true,
                    confirmButtonClass:'btn-danger',
                    cancelButtonClass: 'btn-default ',
                    confirmButton: '删除!',
                    cancelButton: '取消',
                    confirm: function(){
                        ActionassetDelete(select.asset_id)
                    }
                });
            } else {
                MyMessage(0, '请选择资产！');
            }
        }
    } else {
        MyMessage(0, '请选择资产！');
    }
}
function ActionassetDelete(asset_id) {
    if (asset_id) {
        $.ajax({
            url: "/cmdb/asset_manage/fixed_asset/delete_asset/",
            type: 'post',
            data: {'asset_id': asset_id},
            success: function(result) {
                MyMessage(result['code'], result['result']);
                if (result['code'] == 1){
                    $('#table').bootstrapTable("refresh");
                }
            }
        });
    } else {
        MyMessage(0, '请选择资产！');
    }
}

// 删除资产类型
function confirmTypeDelete(){
    var select = getSelectRow();
    if (select && select.type_id) {
        $.confirm({
            title: '提示！',
            content: '确定要删除资产类型「'+select.name+'」吗？',
            closeIcon: true,
            confirmButtonClass:'btn-danger',
            cancelButtonClass: 'btn-default ',
            confirmButton: '删除!',
            cancelButton: '取消',
            confirm: function(){
                $.ajax({
                    url: "/cmdb/asset_manage/fixed_asset/delete_asset_type/",
                    type: 'post',
                    data: {'type_id': select.type_id},
                    success: function(result) {
                        MyMessage(result['code'], result['result']);
                        if (result['code'] == 1){
                            $('#table').bootstrapTable("refresh");
                        }
                    }
                });
            }
        });
    } else {
        MyMessage(0, '请选择资产类型！');
    }
}

// 删除供应商
function confirmSupplierDelete(){
    var select = getSelectRow();
    if (select && select.supplier_id) {
        $.confirm({
            title: '提示！',
            content: '确定要删除供应商「'+select.name+'」吗？',
            closeIcon: true,
            confirmButtonClass:'btn-danger',
            cancelButtonClass: 'btn-default ',
            confirmButton: '删除!',
            cancelButton: '取消',
            confirm: function(){
                $.ajax({
                    url: "/cmdb/asset_manage/fixed_asset/delete_supplier/",
                    type: 'post',
                    data: {'supplier_id': select.supplier_id},
                    success: function(result) {
                        MyMessage(result['code'], result['result']);
                        if (result['code'] == 1){
                            $('#table').bootstrapTable("refresh");
                        }
                    }
                });
            }
        });
    } else {
        MyMessage(0, '请选择供应商！');
    }
}
var tag_mum = 0;
function closeTag(tag_id){
    $("#"+tag_id).remove();
}
function ActionassetTypeAdd() {
    var my_field = [];
    $('#tags').children('span')[0]
    for (i in $('#tags').children('span')){
        span_id = $('#tags').children('span')[i].id;
        if (span_id){
            my_field.push($('#'+span_id+' span').text().replace(/(^\s*)|(\s*$)/g, ""));
        }
    }
    if ($('#asset_type_add_id').val() == ''){
        MyMessage(0, '类型名称不能为空！');
    }else{
        $.ajax({
            url:"/cmdb/asset_type_change",
            type: 'post',
            data: {'asset_type_add_name': $('#asset_type_add_id').val(), 'my_field': my_field+"",
                'asset_form_type_name': $('#asset_form_type_id').val()},
            success: function(result) {
                MyMessage(result['code'], result['result']);
                if (result['code'] == 1){
                    tag_mum = 0;
                    $('#assetTypeAddModal').modal('hide');
                    $('#table').bootstrapTable("refresh");
                }
            }
        });
    }
}
$(function() {
    $(".tags_enter").blur(function() { //焦点失去触发
        var txtvalue=$(this).val().trim();
        if(txtvalue!=''){
            addTag($(this));
            $(this).parents(".type_add_tags").css({"border-color": "#d5d5d5"})
        }
    }).keydown(function(event) {
        var key_code = event.keyCode;
        var txtvalue=$(this).val().trim();
        if (key_code == 13&& txtvalue != '') { //enter
            addTag($(this));
        }
        if (key_code == 32 && txtvalue!='') { //space
            addTag($(this));
        }
    });
    $(".type_add_tags").click(function() {
        $(this).css({"border-color": "#57a3f3"})
    }).blur(function() {
        $(this).css({"border-color": "#d5d5d5"})
    })
});
function addTag(obj) {
    var tag = obj.val().replace(/(^\s*)|(\s*$)/g, "");
    if (tag != '') {
        var i = 0;
        $(".type_add_tag").each(function() {
            if ($(this).text() == tag + "×") {
                $(this).addClass("tag-warning");
                setTimeout("removeWarning()", 400);
                i++;
            }
        });
        obj.val('');
        if (i > 0) { //说明有重复
            return false;
        }
        $("#form-field-tags").before("<span class='type_add_tag' id='type_add_tag_id_"+tag_mum+"'><span>" +
            tag + "</span><button class='close' type='button' onclick='closeTag(\"type_add_tag_id_"+tag_mum+"\")'>×</button></span>"); //添加标签
    }
    tag_mum += 1
}
function removeWarning() {
    $(".tag-warning").removeClass("tag-warning");
}

function ActionassetSupplierChange() {
    if ($('#change_supplier_name_id').val() == ''){
        MyMessage(0, '供应商名称不能为空！');
    }else{
        $.ajax({
            url:"/cmdb/supplier_change",
            type: 'post',
            data: $("#asset_supplier_change_form").serializeArray(),
            success: function(result) {
                MyMessage(result['code'], result['result']);
                if (result['code'] == 1){
                    tag_mum = 0;
                    $('#assetSupplierChangeModal').modal('hide');
                    $('#table').bootstrapTable("refresh");
                }
            }
        });
    }
}

//自定义导出按钮
var TableExport = function() {
    "use strict";
    // function to initiate HTML Table Export
    var runTableExportTools = function() {
        $(".export-excel").on("click", function(e) {
            e.preventDefault();
            var exportTable = $(this).data("table");
            var ignoreColumn = $(this).data("ignorecolumn");
            $(exportTable).tableExport({
                type : 'excel',
                escape : 'false',
                ignoreColumn : '[' + ignoreColumn + ']'
            });
        });
    };
    return {
        // main function to initiate template pages
        init : function() {
            runTableExportTools();
            //runDataTable_example2();
        }
    };
}(jQuery);
TableExport.init();
//下拉选择框初始化
$(".selectpicker").selectpicker({
    noneSelectedText : ''//默认显示内容
});
//获取选择列
function getSelectRow() {
   var getSelectRows = $("#table").bootstrapTable('getSelections', function (row) {
        return row;
    });
   for (i in getSelectRows){
       var row_result = getSelectRows[i]
   }
   return row_result;
}
// 初始化搜索下拉框
$(document).ready(function(){
    initTable();
    $.ajax({
       url: "/cmdb/get_supplier",
       type: "get",
       success: function(result){
           $.each(result.result, function (index, item) {
               $('#supplier_id.selectpicker').append('<option value=' + item['value'] + '>' + item['name'] + '</option>');
           });
           $('#supplier_id').selectpicker('refresh');
       }
    });
    $.ajax({
       url: "/cmdb/get_asset_type",
       type: "get",
       success: function(result){
           $('#custom_export_asset_type_id.selectpicker').append('<option value=""></option>');
           $.each(result.result, function (index, item) {
               $('#asset_type_id.selectpicker').append('<option value=' + item['value'] + '>' + item['name'] + '</option>');
               $('#custom_export_asset_type_id.selectpicker').append('<option value=' + item['value'] + '>' + item['name'] + '</option>');
           });
           $('#asset_type_id').selectpicker('refresh');
           $('#custom_export_asset_type_id.selectpicker').selectpicker('refresh');
       }
    });
    $.ajax({
       url: "/cmdb/get_all_user/",
       type: "get",
       success: function(result){
           $('#operator_id.selectpicker').append('<option></option>');
           $.each(result.result, function (index, item) {
               $('#operator_id.selectpicker').append('<option value=' + item['value'] + '>' + item['name'] + '</option>');
           });
           $('#operator_id').selectpicker('refresh');
       }
    });
    $.ajax({
        url: "/cmdb/get_org/",
        type: "post",
        async: false,
        success: function (result) {
            if (result['result']) {
                for (i in result['result']) {
                    if (result['result'][i]['id'] == 1) {
                        result['result'][i]['open'] = 'true';
                        break
                    }
                }
                zTreeObj = $.fn.zTree.init($("#treeDemo"), setting, result['result']);
            }
        }
    });
});
// 组织结构树
var zTreeObj;
var setting = {
    data: {
        simpleData: {
            enable: true,
            idKey: "id",
            pIdKey: "parentid",
            rootPId: 0
        }
    },
    check: {
        enable: true
    },
    callback: {
        onClick: zTreeOnClick
    }
};
function zTreeOnClick(event, treeId, treeNode){
    $('#orgModal').modal('hide');
    $("#org_search_input_id").val(treeNode.name);
}

function viewsCutover(id) {
    if (id == 1) {
        $('#table').bootstrapTable('refreshOptions', {
            url : "/cmdb/asset_manage/fixed_asset/fixed_asset_list/",
            pagination: true,
            detailView:true,
            pageNumber:1,
            columns: [
            {
                title:'',
                field:'select',
                checkbox:true,
                width:20,
                align:'center',
                valign:'middle'
            },
            {
                title:'资产编号',
                field:'asset_id',
                sortable:true
            },
            {
                title:'SN',
                field:'sn',
                sortable:false
            },
            {
                title:'资产类型',
                field:'asset_type',
                sortable:true
            },
            {
                title:'操作人',
                field:'operator',
                sortable:true
            },
            {
                title:'操作时间',
                field:'operate_time',
                sortable:true
            },
            {
                title:'采购日期',
                field:'buy_time',
                sortable:true
            },
            {
                title:'供应商',
                field:'supplier',
                sortable:true
            },
            {
                title:'领用人',
                field:'use_person',
                sortable:true
            },
            {
                title:'领用时间',
                field:'use_time',
                sortable:true
            },
            {
                title:'资产状态',
                field:'status',
                sortable:true
            },
            {
                title:'备注',
                field:'remark',
                sortable:true,
                width:250
            }],
            detailFormatter:function (index, row) {
            var detail_info = '';
            $.ajax({
                url: "/cmdb/get_asset_detail/",
                type: "post",
                async : false,
                data: {'asset_id': row.asset_id },
                success: function (result) {
                    detail_info = result['result']
                }
            });
            return detail_info
        }});
        document.getElementById("searchAssetId").style.display = "block";
        document.getElementById("asset_search_btid").className = "ivu-btn ivu-btn-primary";
        document.getElementById("asset_type_btid").className = "ivu-btn ivu-btn-ghost";
        document.getElementById("asset_supplier_btid").className = "ivu-btn ivu-btn-ghost";
        document.getElementById("asset_bt_group").style.display = "block";
        document.getElementById("type_bt_group").style.display = "none";
        document.getElementById("supplier_bt_group").style.display = "none";
    } else if (id == 2) {
        $('#table').bootstrapTable('refreshOptions', {
            url : "/cmdb/asset_manage/fixed_asset/asset_type_list/",
            pagination: true,
            detailView:false,
            pageNumber:1,
            columns: [
            {
                title:'',
                field:'select',
                checkbox:true,
                width:20,
                align:'center',
                valign:'middle'
            },
            {
                title:'类型ID',
                field:'type_id',
                sortable:false
            },
            {
                title:'类型名称',
                field:'name',
                sortable:false
            },
            {
                title:'自定义资产字段',
                field:'customize_asset_field',
                sortable:false
            }]
        });
        document.getElementById("searchAssetId").style.display= "none";
        document.getElementById("asset_type_btid").className = "ivu-btn ivu-btn-primary";
        document.getElementById("asset_search_btid").className = "ivu-btn ivu-btn-ghost";
        document.getElementById("asset_supplier_btid").className = "ivu-btn ivu-btn-ghost";
        document.getElementById("asset_bt_group").style.display = "none";
        document.getElementById("type_bt_group").style.display = "block";
        document.getElementById("supplier_bt_group").style.display = "none";
    } else if (id == 3) {
        $('#table').bootstrapTable('refreshOptions', {
            url : "/cmdb/asset_manage/fixed_asset/supplier_manage_list/",
            pagination: true,
            detailView:false,
            pageNumber:1,
            columns: [
            {
                title:'',
                field:'select',
                checkbox:true,
                width:20,
                align:'center',
                valign:'middle'
            },
            {
                title:'供应商ID',
                field:'supplier_id',
                sortable:false
            },
            {
                title:'供应商名称',
                field:'name',
                sortable:false
            },
            {
                title:'联系人',
                field:'contact',
                sortable:false
            },
            {
                title:'固定电话',
                field:'fixed_telephone',
                sortable:false
            },
            {
                title:'手机号码',
                field:'mobile_phone',
                sortable:false
            },
            {
                title:'地址',
                field:'address',
                sortable:false
            },
            {
                title:'邮箱',
                field:'email',
                sortable:false
            },
            {
                title:'QQ',
                field:'qq',
                sortable:false
            },
            {
                title:'备注',
                field:'remark',
                sortable:false,
                width:250
            }]
        });
        document.getElementById("searchAssetId").style.display= "none";
        document.getElementById("asset_type_btid").className = "ivu-btn ivu-btn-ghost";
        document.getElementById("asset_search_btid").className = "ivu-btn ivu-btn-ghost";
        document.getElementById("asset_supplier_btid").className = "ivu-btn ivu-btn-primary";
        document.getElementById("asset_bt_group").style.display = "none";
        document.getElementById("type_bt_group").style.display = "none";
        document.getElementById("supplier_bt_group").style.display = "block";
    }
}

$("#searchAssets").on("click", function () {
    searchTable('table','searchAssetId')
});
function formReset() {
    document.getElementById("searchAssetId").reset();
    $(".selectpicker").selectpicker('refresh');
}
// 资产查询数据
function initTable() {
    $('#table').bootstrapTable({
        method: "post",  //使用post请求到服务器获取数据
        contentType: "application/x-www-form-urlencoded; charset=UTF-8",//必须要有
        dataType: "json",
        cache: false,
        url:'/cmdb/asset_manage/fixed_asset/fixed_asset_list/',
        toolbar: '#toolbar',//指定工具栏
        striped: true,  //表格显示条纹
        minimumCountColumns: 1,
        dataField: "rows",
        pagination: true, //启动分页
        sortable: true,  //启用排序
        pageSize: 15,  //每页显示的记录数
        pageNumber:1, //当前第几页
        pageList: [5, 10, 15, 20, 25, 'All'],  //记录数可选列表
        search: false,  //是否启用查询
        searchOnEnterKey:true, //设置为 true时，按回车触发搜索方法，否则自动触发搜索方法
        searchAlign:'left', //指定 搜索框 水平方向的位置。’left’ or ‘right’
        showColumns: false,  //显示下拉框勾选要显示的列
        showRefresh: false,  //显示刷新按钮
        showSearchButton: false, //显示搜索按钮
        showExport: false,//显示导出按钮
        exportDataType: "all", //'basic'导出当前页, 'all'导出所有数据, 'selected'导出选中的数据.
        sidePagination: "server", //表示服务端请求
        //设置为undefined可以获取pageNumber，pageSize，searchText，sortName，sortOrder
        //设置为limit可以获取limit, offset, search, sort, order
        queryParamsType : "undefined",
        clickToSelect: true,//是否启用点击选中行
        singleSelect:true, // 设置 true 将禁止多选
        checkboxHeader:false, //设置 false 将在列头隐藏全选复选框
        toolbarAlign:'left',//工具栏对齐方式
        buttonsAlign:'right',//按钮对齐方式
        detailView:true,
        columns:[
            {
                title:'',
                field:'select',
                checkbox:true,
                width:20,
                align:'center',
                valign:'middle'
            },
            {
                title:'资产编号',
                field:'asset_id',
                sortable:true
            },
            {
                title:'SN',
                field:'sn',
                sortable:false
            },
            {
                title:'资产类型',
                field:'asset_type',
                sortable:true
            },
            {
                title:'操作人',
                field:'operator',
                sortable:true
            },
            {
                title:'操作时间',
                field:'operate_time',
                sortable:true
            },
            {
                title:'采购日期',
                field:'buy_time',
                sortable:true
            },
            {
                title:'供应商',
                field:'supplier',
                sortable:true
            },
            {
                title:'领用人',
                field:'use_person',
                sortable:true
            },
            {
                title:'领用时间',
                field:'use_time',
                sortable:true
            },
            {
                title:'资产状态',
                field:'status',
                sortable:true
            },
            {
                title:'备注',
                field:'remark',
                sortable:true,
                width:250
            }
        ],
        queryParams: function queryParams(params) {   //设置查询参数
            var param = {
                csrfmiddlewaretoken :$("input[name='csrfmiddlewaretoken']").val(),
                pageNumber: params.pageNumber,
                pageSize: params.pageSize,
                search:params.searchText,
                order:params.sortOrder,
                sort:params.sortName
            };
            return param;
        },
        detailFormatter:function (index, row) {
            var detail_info = '';
            $.ajax({
                url: "/cmdb/get_asset_detail/",
                type: "post",
                async : false,
                data: {'asset_id': row.asset_id },
                success: function (result) {
                    detail_info = result['result']
                }
            });
            return detail_info
        }
    });
}

$('.timeselect_input').daterangepicker({
  minDate: '01/01/2000',    //最小时间
  showDropdowns : true,
  showWeekNumbers : false, //是否显示第几周
  timePicker : false, //是否显示小时和分钟
  timePickerIncrement : 1440, //时间的增量，单位为分钟
  timePicker12Hour : false, //是否使用12小时制来显示时间
  opens : 'right', //日期选择框的弹出位置
  buttonClasses : [ 'ivu-btn' ],
  applyClass : 'ivu-btn-primary',
  cancelClass : 'ivu-btn-ghost',
  format : 'YYYY-MM-DD', //控件中from和to 显示的日期格式
  separator : 'to',
  locale : {
      format : 'YYYY-MM-DD',
      separator: '~',
      applyLabel : '确定',
      cancelLabel : '取消',
      resetLabel: "重置",
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
});
$('.timeselect_input').val('');

$('#myModal').on('show.bs.modal', function (event) {
    var asset_type_dict = {};
    var supplier_dict = {};
    var status_dict = {'在库': 1, '借出': 2, '维修': 3, '报废': 4};
    $('#add_status_id.selectpicker').selectpicker('refresh');
    $('#add_asset_type_id.selectpicker').empty();
    $('#add_asset_type_id.selectpicker').append('<option></option>');
    $.ajax({
       url: "/cmdb/get_asset_type",
       type: "get",
       async: false,
       success: function(result){
           $.each(result.result, function (index, item) {
               $('#add_asset_type_id.selectpicker').append('<option value=' + item['value'] + '>' + item['name'] + '</option>');
               asset_type_dict[item['name']] = item['value']
           });
           $('#add_asset_type_id').selectpicker('refresh');
       }
    });
    $('#add_supplier_id.selectpicker').empty();
    $('#add_supplier_id.selectpicker').append('<option></option>');
    $.ajax({
       url: "/cmdb/get_supplier",
       type: "get",
       async: false,
       success: function(result){
           $.each(result.result, function (index, item) {
               $('#add_supplier_id.selectpicker').append('<option value=' + item['value'] + '>' + item['name'] + '</option>');
               supplier_dict[item['name']] = item['value']
           });
           $('#add_supplier_id').selectpicker('refresh');
       }
    });

    jeDate("#add_buydate_id",{
        format:"YYYY-MM-DD",
        isTime:false,
        minDate:"2000-01-01 00:00:00"
    });

    var a = $(event.relatedTarget).data('id');
    if (a) {
        $('#change_asset_title_id').html('修改资产');
        var select = getSelectRow();
        if (select && select.asset_id) {
            $("#hidden_add_asset_id").val(select.asset_id);
            $("#add_asset_id").val(select.asset_id);
            $("#add_asset_id").attr('readOnly','false');
            $("#add_buydate_id").val(select.buy_time);
            $("#add_remark_id").val(select.remark);
            $('#add_asset_type_id').selectpicker('val', asset_type_dict[select.asset_type]);
            $('#add_asset_type_id').selectpicker('refresh');
            $('#add_supplier_id').selectpicker('val', supplier_dict[select.supplier]);
            $('#add_supplier_id').selectpicker('refresh');
            $('#add_status_id').selectpicker('val', status_dict[select.status]);
            $('#add_status_id').selectpicker('refresh');
            $.ajax({
                url: "/cmdb/asset_manage/fixed_asset/get_asset_field/",
                type: "post",
                data: {'type_id': asset_type_dict[select.asset_type],'asset_id':select.asset_id},
                success: function(result) {
                    $("#add_my_field_group").empty();
                    if (result['the_value']){
                        var my_alert_field_num = 0;
                        for (i in result['the_value']){
                            if (result['the_value'][i]) {
                                var the_value = result['the_value'][i]
                            } else {
                                var the_value = ''
                            }
                            my_alert_field_num += 1;
                            $("#add_my_field_group").append('\
                            <div class="form-group" id="my_field_'+my_alert_field_num+'">\
                                <label class="ivu-form-item-label pull-left col-md-2">'+i+'</label>\
                                <div class="col-md-10 col-sm-10 col-xs-10" style="padding-right:0">\
                                <input class="ivu-input" required="required" type="text" autocomplete="off" value="'+the_value+'" \
                                name="'+i+'" id="my_field_value_'+my_alert_field_num+'"></div>\
                            </div>')
                        }
                    }
                }
            })
        } else {
            MyMessage(0, '请选择资产！');
            return false;
        }
    } else {
        $('#change_asset_title_id').html('添加资产');
        return true;
    }
});
$('#myModal').on('hidden.bs.modal', function () {
    document.getElementById("add_asset_form").reset();
    $("#hidden_add_asset_id").val('');
    $("#add_my_field_group").empty();
    $("#add_item_group").empty();
    $("#add_asset_id").removeAttr("readOnly");
});
$('#assetOutModal').on('hidden.bs.modal', function () {
    document.getElementById("asset_out_form").reset();
    $('#asset_use_person_id').selectpicker('refresh');
});
$('#assetBackModal').on('hidden.bs.modal', function () {
    document.getElementById("asset_back_form").reset();
    $('#asset_back_person_id').selectpicker('refresh');
});
$('#assetMaintainModal').on('hidden.bs.modal', function () {
    document.getElementById("asset_maintain_form").reset();
    $("#asset_maintain_person_id").removeAttr('readOnly');
});
$('#assetTypeAddModal').on('hidden.bs.modal', function () {
    $("#asset_form_type_id").val('');
    document.getElementById("asset_type_add_form").reset();
    $("#tags span").remove();
});
$('#assetTypeAddModal').on('show.bs.modal', function (event) {
    var a = $(event.relatedTarget).data('id');
    if (a) {
        var select = getSelectRow();
        if (select && select.type_id) {
            $("#type_title_id").html('修改资产类型');
            $("#asset_form_type_id").val(select.type_id);
            $("#asset_type_add_id").val(select.name);
            if (select.customize_asset_field) {
                var tag_mum = 999;
                for (tag in select.customize_asset_field.split(",")) {
                    $("#form-field-tags").before("<span class='type_add_tag' id='type_add_tag_id_" + tag_mum + "'><span>" +
                        select.customize_asset_field.split(",")[tag] + "</span><button class='close' type='button' onclick='closeTag(\"type_add_tag_id_" + tag_mum + "\")'>×</button></span>"); //添加标签
                    tag_mum += 1
                }
            }
        } else {
            MyMessage(0, '请选择资产类型！');
            return false;
        }
    } else {
        $("#type_title_id").html('添加资产类型');
    }
});
$('#assetSupplierChangeModal').on('hidden.bs.modal', function () {
    $("#change_supplier_id").val('');
    document.getElementById("asset_supplier_change_form").reset();
});
$('#assetSupplierChangeModal').on('show.bs.modal', function (event) {
    var a = $(event.relatedTarget).data('id');
    if (a) {
        var select = getSelectRow();
        if (select && select.supplier_id) {
            $("#supplier_title_id").html('修改供应商信息');
            $("#change_supplier_id").val(select.supplier_id);
            $("#change_supplier_name_id").val(select.name);
            $("#change_supplier_contact_id").val(select.contact);
            $("#change_supplier_fixed_telephone_id").val(select.fixed_telephone);
            $("#change_supplier_mobile_phone_id").val(select.mobile_phone);
            $("#change_supplier_address_id").val(select.address);
            $("#change_supplier_email_id").val(select.email);
            $("#change_supplier_qq_id").val(select.qq);
            $("#change_supplier_remark_id").val(select.remark);
        } else {
            MyMessage(0, '请选择供应商！');
            return false;
        }
    } else {
        $("#supplier_title_id").html('添加供应商');
    }
});
$('#CountModal').on('show.bs.modal', function () {
    $.ajax({
        url: "/cmdb/asset_manage/fixed_asset/asset_count/",
        type: "post",
        success: function(result) {
            var the_table = '';
            for (i in result['result']) {
                the_table += '<tr><td>'+i+'</td>' +
                    '<td>'+result['result'][i]['在库']+'</td>' +
                    '<td>'+result['result'][i]['借出']+'</td>' +
                    '<td>'+result['result'][i]['维修']+'</td>' +
                    '<td>'+result['result'][i]['报废']+'</td>' +
                    '<td>'+result['result'][i]['统计']+'</td></tr>'
            }
            $("#asset_count_tbody_id").html(the_table);
        }
    })
});

$('#custom_export_asset_type_id').change(function(e){
    $.ajax({
        url: "/cmdb/asset_manage/fixed_asset/get_asset_field/",
        type: "post",
        data: {'type_id': e.target.value},
        success: function(result) {
            if (result['result']){
                var ob = $('#custom_export_field_id.selectpicker');
                document.getElementById("custom_export_field_id").options.length=0;
                ob.append('<option value="asset_id">资产编号</option>');
                ob.append('<option value="asset_type">资产类型</option>');
                ob.append('<option value="operator">操作人</option>');
                ob.append('<option value="operate_time">操作时间</option>');
                ob.append('<option value="buy_time">采购日期</option>');
                ob.append('<option value="supplier">供应商</option>');
                ob.append('<option value="use_person">领用人</option>');
                ob.append('<option value="use_time">领用时间</option>');
                ob.append('<option value="status">资产状态</option>');
                ob.append('<option value="remark">备注</option>');
                for (i in result['result']){
                    ob.append('<option value=' + result['result'][i] + '>' + result['result'][i] + '</option>');
                }
                ob.selectpicker('refresh');
            }
        }
    })
});

function CustomExportSubmit() {
    if (!$('#custom_export_asset_type_id').val()){
        MyMessage(0, '请选择资产类型！');
        return false
    } else if(!$('#custom_export_field_id').val()) {
        MyMessage(0, '请选择导出字段！');
        return false
    }
    var custom_export_form = $('#custom_export_form_id').serializeArray();
    $('#export_loading_id').show();
    $.ajax({
        url: "/cmdb/asset_manage/fixed_asset/custom_export/",
        type: "post",
        data: custom_export_form,
        success: function(result){
            if (result['result']['data_list']){
                var option={};
                option.fileName = '固定资产导出';
                option.datas=[{
                    sheetFilter:result['result']['field'],
                    sheetHeader:result['result']['field'],
                    sheetData:result['result']['data_list'],
                }];
                var toExcel=new ExportJsonExcel(option);
                try{toExcel.saveExcel();MyMessage(1, '导出成功！');}
                catch(err){MyMessage(2, '无数据！');}

            } else {
                MyMessage(2, '无数据！');
            }
            $('#export_loading_id').hide();
        },
        error: function(result){
            MyMessage(0, result.responseText);
            $('#export_loading_id').hide();
        }
    })
}
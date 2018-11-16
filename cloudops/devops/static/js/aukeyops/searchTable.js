/**
 * Created by User on 2018/5/15.
 */

// Post搜索
var searchTable = function (tableId, searchFormID){
    var params = $('#'+tableId).bootstrapTable('getOptions');
    params.queryParams = function(params) {
        var search = {};
        if (params['sortOrder'] == 'desc') {
            params['sortName'] = '-'+params['sortName']
        }
        params['page'] = params['pageNumber']
        params['size'] = params['pageSize']
        params['ordering'] = params['sortName']
        
        $.each($("#"+searchFormID).serializeArray(), function (i, field) {
            if (null!=field.value && ""!=field.value){
                if (params[field.name]){
                    params[field.name] += ","+field.value.replace(/(^\s*)|(\s*$)/g, "");
                }else{
                    params[field.name] = field.value.replace(/(^\s*)|(\s*$)/g, "");
                }
            }
        });
        return params;
    };
    $('#'+tableId).bootstrapTable('refresh', params);
};

// url搜索
var searchGetTable = function(tableId, searchFormID, url){
    var search_params = '?' + $("#"+searchFormID).serialize();
    $('#'+tableId).bootstrapTable('refreshOptions', {
        pageNumber:1,
        url: url + search_params
    });
};
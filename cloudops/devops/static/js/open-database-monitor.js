function jump_queries_analyzing(){
        $.ajax({
            type: "get",
            url: "/database/instance/jump_queries_analyzing",
            dataType: "json",
            success: function(result) {
                if(result = 'true'){
                    var tempwindow=window.open();
                    tempwindow.location='http://10.1.3.126:10010/graph/dashboard/db/_pmm-query-analytics?orgId=1&var-host=baiy-3306';
                }
            },
            error:function(){
                new PNotify({
                  title: 'error',
                  text: '没有访问权限!',
                  type: 'error',
                  styling: 'bootstrap3'
                });
            }
        });
    }
    function jump_monitor(){
        $.ajax({
            type: "get",
            url: "/database/instance/jump_monitor",
            dataType: "json",
            success: function(result) {
                if(result = 'true'){
                    var tempwindow=window.open();
                    tempwindow.location='http://10.1.3.126:10010/graph/dashboard/db/cross-server-graphs?refresh=1m&orgId=1';
                }
            },
            error:function(){
                new PNotify({
                  title: 'error',
                  text: '没有访问权限!',
                  type: 'error',
                  styling: 'bootstrap3'
                });
            }
        });
    }
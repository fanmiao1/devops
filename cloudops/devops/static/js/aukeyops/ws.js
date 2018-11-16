/**
 * Author:Xieyz
 * Created by User on 2018/2/9.
 */
var wscc;
function WebSocketStart(connect_arg, container_id) {
    var term;
    url = "ws://codeops.aukeyit.com/webssh/?uid="+connect_arg.uid+"&sid="+connect_arg.sid+"&inoex="+connect_arg.inoex+"&cid="+connect_arg.cid;
    // var ws = new WebSocket("ws://codeops.aukeyit.com/websocket/chart/push/sid="+connect_arg.sid+"/inoex="+connect_arg.inoex+"/cid="+connect_arg.cid+"/");
    var ws = new WebSocket(url);
    wscc = ws;
    if ("WebSocket" in window) {
       // 打开一个 web socket
       ws.onopen = function(evt) {
            term = new Terminal({  //new 一个terminal实例，就是数据展示的s屏幕和一些见简单设置，包括屏幕的宽度，高度，光标是否闪烁等等
          //    cols: 300,
          　　rows: 35,
          // 　　screenKeys: true,
          // 　　useStyle: true,
          　　cursorBlink: true,
             // visualBell:true,
             // convertEol:true,
             // termName:'xterm',
             // popOnBell:true,
             // debug:false
            });
            // ws.send(connect_arg);
        　　/*term实时监控输入的数据，并且websocket把实时数据发送给后台*/
            term.on('data', function(data) {//term.on方法就是实时监控输入的字段，
                ws.send(data);
            });
            term.on('title', function(title) {
              // document.title = title;
            });
            term.open(document.getElementById(container_id));//屏幕将要在哪里展示，就是屏幕展示的地方
            ws.onmessage = function(evt) {//接受到数据
　　          　 term.write(evt.data);//把接收的数据写到这个插件的屏幕上
                if (evt.data == '连接失败') {
                    alert('连接失败，请检查实例和凭证')
                }
            };
            ws.onclose = function(evt) {//websocket关闭
          　　term.write("Session terminated");
          　　term.destroy();//屏幕关闭
            };
            ws.onerror = function(evt) {//失败额处理
          　　if (typeof console.log == "function") {
            　　　　console.log(evt)
          　　}
            }
       };
        var close = function() {//关闭websocket
            ws.close();
        };
    }
    else {
       // 浏览器不支持 WebSocket
       alert("您的浏览器不支持 WebSocket!");
    }
 }


function WebSocketStop() {
    try {
        console.log('Close connection!');
        wscc.send('quit');
        wscc.close();
        wscc = null;
        $('#termTab').html('');
        $('#termTabContent').html('');
    }
    catch (ex) {
        console.log(ex);
    }
}
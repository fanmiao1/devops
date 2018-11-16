/**
 * Created by User on 2018/7/6.
 */
    function WebSocketTest() {
        if ("WebSocket" in window) {
            console.log("您的浏览器支持 WebSocket!");

            // 打开一个 web socket
            var ws = new WebSocket("ws://"+ window.location.host +"/chart/ws_public/");

            ws.onopen = function()
            {
              // Web Socket 已连接上，使用 send() 方法发送数据
              console.log("数据发送中...");
              ws.send("hello world")
            };

            ws.onmessage = function (evt)
            {
              var received_msg = evt.data;
              MyMessage(1, received_msg);
              console.log(received_msg)
            };

            ws.onclose = function()
            {
              // 关闭 websocket
              console.log("连接已关闭...");
            };
        }
        else
        {
           // 浏览器不支持 WebSocket
           console.log("您的浏览器不支持 WebSocket!");
        }
    }
    WebSocketTest();
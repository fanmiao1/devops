var jQuery;
var wssh = {};
var status = $('#status'),
    btn = $('.btn-primary'),
    style = {};

function parse_xterm_style() {
  var text = $('.xterm-helpers style').text();
  var arr = text.split('xterm-normal-char{width:');
  style.width = parseFloat(arr[1]);
  arr = text.split('div{height:');
  style.height = parseFloat(arr[1]);
}


function current_geometry() {
  if (!style.width || !style.height) {
    parse_xterm_style();
  }
  var cols = parseInt(window.innerWidth / style.width, 10) - 1;
  var rows = parseInt(window.innerHeight / style.height, 10);
  return {'cols': cols, 'rows': rows};
}

function resize_term(term, sock) {
  var geometry = current_geometry(),
      cols = geometry.cols,
      rows = geometry.rows;
  if (cols !== term.geometry[0] || rows !== term.geometry[1]) {
    console.log('resizing term');
    term.resize(cols, rows);
  }
}

function callback(msg,connect_arg='',container_id='') {
    url = "ws://codeops.aukeyit.com/webssh/?uid="+connect_arg.uid+"&sid="+connect_arg.sid+"&inoex="+connect_arg.inoex+"&cid="+connect_arg.cid;
    sock = new window.WebSocket(url);
    encoding = 'UTF-8';
    terminal = document.getElementById('#'+container_id);
    term = new window.Terminal({
      cursorBlink: true
    });

  wssh.sock = sock;
  wssh.term = term;

  term.on('data', function(data) {
    sock.send(data);
  });

  sock.onopen = function() {
    $('.container').hide();
    term.open(terminal, true);
    term.toggleFullscreen(true);
  };

  sock.onmessage = function(evt) {
　　   term.write(evt.data);
      if (!term.resized) {
        resize_term(term, sock);
        term.resized = true;
      }
      if (evt.data == '连接失败') {
          alert('连接失败，请检查凭证!')
      }
  };

  sock.onerror = function(e) {
    console.log(e);
  };

  sock.onclose = function(e) {
    console.log(e);
    term.destroy();
    wssh.term = undefined;
    wssh.sock = undefined;
    $('.container').show();
    status.text(e.reason);
    btn.prop('disabled', false);
  };
}

$(window).resize(function(){
  if (wssh.term && wssh.sock) {
    resize_term(wssh.term, wssh.sock);
  }
});

function WebSocketStart(connect_arg, container_id) {
    callback('',connect_arg, container_id);
}

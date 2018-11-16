// 消息弹框
function MyMessage(TYPE, TEXT) {
    if (TYPE == 1) {
        new PNotify({
            title: 'SUCCESS',
            text: TEXT,
            type: 'success',
            styling: 'bootstrap3'
        });
    } else if (TYPE == 2) {
        new PNotify({
            title: 'WARNING',
            text: TEXT,
            type: 'warning',
            styling: 'bootstrap3'
        });
    } else {
        new PNotify({
            title: 'ERROR',
            text: TEXT,
            type: 'error',
            styling: 'bootstrap3'
        });
    }
}
/**
 *
 * Date :2018.1.5
 * Author: cy
 */
// window.onload = function () {
//  loadContant();
// }

function loadContant(a) {
 // a.click(function () {
 //  // $('.main-container').load($(this)[0].dataset.url);
 //  window.location.href = a[0].dataset.url;
 // })
};
$('.sidebar-menu a.submenu-label').click(function () {
 loadContant($(this));
})
$("#logoBox").click(function () {
 loadContant($(this));
})


/**
 *
 * Date :2018.2.2
 * Author: Xieyz
 */

//解决django下ajax传输不被允许
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
    var csrftoken = getCookie('csrftoken');
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/* center modal */
function centerModals(){
    $('.modal').each(function(i){
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top);
    });
}
$('.modal').on('show.bs.modal', centerModals);
$(window).on('resize', centerModals);

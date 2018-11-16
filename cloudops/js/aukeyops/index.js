/**
 *
 * Date :2018.1.8
 * Author: cy
 * 
 */
window.onload = function () {
 loadContant();
}

function loadContant() {
 $('.sidebar-menu a.submenu-label').click(function () {
  // $('.main-container').load($(this)[0].dataset.url);
  window.location.href = $(this)[0].dataset.url;
  $(".sidebar-menu li").removeClass("active");
  $(this).parent('li').addClass("active");
 })

};
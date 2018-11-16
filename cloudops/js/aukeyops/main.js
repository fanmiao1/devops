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
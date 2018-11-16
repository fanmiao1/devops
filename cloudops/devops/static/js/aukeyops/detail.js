/**
 *
 * Date :2018.3.2
 * Author: Xieyz
 */

// 收起过长的文字
if($("#desc_maxlenght").length>0){
    function show(){
        var box = document.getElementById("desc_maxlenght");
        var text = box.innerHTML;
        var newBox = document.createElement("div");
        var btn = document.createElement("a");
        newBox.innerHTML = text.substring(0,200);
        btn.innerHTML = text.length > 200 ? "...显示全部" : "";
        btn.href = "###";
        btn.className = "btn btn-link";
        btn.onclick = function(){
            if (btn.innerHTML == "...显示全部"){
                btn.innerHTML = "收起";
                newBox.innerHTML = text;
            }else{
                btn.innerHTML = "...显示全部";
                newBox.innerHTML = text.substring(0,200);
            }
            PostbirdImgGlass.init({
                domSelector:"img",
                animation:true
            });
        };
        box.innerHTML = "";
        box.appendChild(newBox);
        box.appendChild(btn);
    }
    show();
}
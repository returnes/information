function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();
        var old_password=$('.old_pass1').val()
        var new_password1=$('.new_pass1').val()
        var new_password2=$('.new_pass2').val()
        var params={
            'old_password':old_password,
            'new_password1':new_password1,
            'new_password2':new_password2
        }
        //  修改密码
         $(this).ajaxSubmit({
             url: "/profile/pass_info",
             type: "POST",
             headers: {
                 "X-CSRFToken": getCookie('csrf_token')
             },
             data:JSON.stringify(params),
             success:function (data) {
                 if(data.errno=='0'){
                     alert(data.errmsg)
                     location.reload()
                 }else {
                     alert(data.errmsg)
                 }
             }

         })
    })
})
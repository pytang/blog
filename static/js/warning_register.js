$(function () {
    //声明一个变量用来记录loginname的存在状态
   var nameStatus = 1;
   //声明一个变量用来记录loginpwd的存在状态
    var pwdStatus = 1;
   //点击btnlogin时跳转到login地址
    $("#btnlogin").click(function () {
        
        location.href='/login';
    });
    //为name=loginname的框绑定blur事件
    function panduanmima (){
        var password = $("[name='loginpwd']").val();
        var cpassword = $("[name='logincpwd']").val();
        if (password == cpassword){
            return 0;
        }else{
            return 1;
        }
    };

    $("[name='loginname']").blur(function () {
        if ($(this).val().trim().length == 0)
            return;
        $.get('/check_loginname',{
            'loginname':$(this).val()
        },function (data) {
            $(".warning_name").html(data.msg);
            nameStatus = data.status;
        },'json')
    });
    //为name=logincpwd的框绑定blur事件
    $("[name='logincpwd']").blur(function () {
        if ($("[name='loginpwd']").val().trim().length == 0){}else{
            mimaStatus = panduanmima();
            if (mimaStatus == 0){
            //返回值为0，判断通过
                $(".warning_pwd").html("通过")
                pwdStatus = 0
            }else{
            //不通过
                $(".warning_pwd").html("两次密码不一致，请重新输入");
                pwdStatus = 1
            }
        }
    });
    //为表单绑定submit事件
    $("#formReg").submit(function () {
        if (nameStatus == 1){
            return false;
        }
        if (pwdStatus == 1){
            return false;
        }
        return true;
    });
});
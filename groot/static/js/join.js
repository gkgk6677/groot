    var idFlag = false;
    var pwFlag = false;
    var authFlag = false;


    $(document).ready(function(){
            defaultScript();

            //region unreal id
            $("#idck").click(function(){
                idFlag = false;
                checkId("first");
            });

            $("#user_pw1").blur(function(){
                pwFlag = false ;
                checkPswd1();
            }).keyup(function(event){
    //        키보드 눌러진상태에서 손 뗄떼
                checkShiftUp(event);
            }).keypress(function(event){
    //        키보드를 누르는 순간. 키 누르고 있을때 한번 시행
                checkCapslock(event);
            }).keydown(function(){
    //        키보드 누르는 순간, 키 누르고 있을때 계속 시행
                checkShiftDown(event);
            });

            $("#user_pw2").keyup(function(event) {
                checkPswd2();
            }).blur(function(){
                checkspace();
            });

            $("#com_name").blur(function() {
                checkcomName();
            });

            $("#com_head").blur(function() {
                checkcomheadName();
            });

            $("#com_ck").click(function(){
                cidFlag = false;
                checkcomId("first");
            });

            $("#email").keyup(function() {
                checkEmail();
            });

            $("#btnJoin").click(function(event) {
                submitClose();
                if(idFlag && pwFlag && cidFlag) {
                    mainSubmit();
                } else {
                    setTimeout(function() {
                        mainSubmit();
                    }, 700);
                }
            });


    });

    function mainSubmit() {
        if (!checkUnrealInput()) {
                submitOpen();
                return false;
        }


        if(idFlag && pwFlag && cidFlag) {
                $("#join_form").submit();}
//				$.ajax({
//					url: '/join',
//					type: 'post',
//					data: $('form').serialize(),
//					success: function(response) {
//                            alert(response.user_id);
////                            var data = JSON.parse(response);
//
//                            var html = '';
//                            html += '<div>'+ data.user_id + '"님 환영합니다." <div>"';
//                            html += '<a href="login">로그인하러가기</a>';
//
//                            $("#join_form_col").empty();
//                            $("#join_form_col").after(html);

//                     error : function(request, status, error){
//						console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error.status);
////					}
//            });
//            return false;


    }

    function checkUnrealInput() {
        if (checkId('join')
                & checkPswd1()
                & checkPswd2()
                & checkEmail()
                & checkcomName()
                & checkcomheadName()
                & checkcomId()
        ) {
            return true;
        } else {
            return false;
        }
    }


    function checkId(event){
        if(idFlag) return true;

        var id = $("#user_id").val();
        var oMsg = $("#idMsg");

        if ( id == "" ){
            showErrorMsg(oMsg, "필수 정보입니다")
            return false;
        }

        var isId = /^[a-z0-9][a-z0-9]{4,19}$/;
        if (!isId.test(id)){
            showErrorMsg(oMsg, "5~20자의 영문 소문자, 숫자만 사용 가능합니다.");
            return false;
        }

        idFlag = false;
        $.ajax({
            type: "post",
            url: "/idcheck",
            data : {'userid':id },
            dataType: "json",
            success : function(response){
                    if (response.ck_val==0){
                        if (event =="first"){
                            showSuccessMsg(oMsg, "사용할 수 있는 아이디입니다.")
                        }else{
                            hideMsg(oMsg);
                        }
                        idFlag = true;
                    } else {
                           showErrorMsg(oMsg, "이미 사용중이거나 탈퇴한 아이디입니다.");
                    }
            },
            error : function(request, status, error){
                            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error.status);
                        }
        });
        return true;

    }


    function checkPswd1() {
        if(pwFlag) return true;

        var pw = $("#user_pw1").val();
        var oMsg = $("#pswd1Msg");

        if (pw == ""){
            showErrorMsg(oMsg, "필수 정보입니다.");
            return false;
        }
        if (isValidPasswd(pw) != true){
            showErrorMsg(oMsg, "8~16자 영문 소문자,숫자를 사용하세요.");
            return false;
        }

    }

    function checkspace(){
        var pswd2 = $("#user_pw2").val();
        var oMsg = $("#pswd2Msg");

        if (pswd2 == ""){
            showErrorMsg(oMsg, "필수 정보입니다.");
            return false;
        }

    }

	function checkPswd2(){

        var pswd1 = $("#user_pw1").val();
        var pswd2 = $("#user_pw2").val();
        var oMsg = $("#pswd2Msg");

		if (pswd1 != pswd2){
			$("#user_pw2").css("background-color", "#FFCECE");
			showErrorMsg(oMsg,"비밀번호가 일치하지 않습니다.");
			return false;
		} else {
			$("#user_pw2").css("background-color", "#f9f9ff");
			hideMsg(oMsg);
            return true;
        }

        return true;

	};

    function checkcomName(){
        var oMsg = $("#com_nameMsg");
        var com_name = $("#com_name").val();

        if (com_name == "") {
            showErrorMsg(oMsg,"필수 정보입니다.");
            return false;
        }

        hideMsg(oMsg);
        return true;
    }

    function checkcomheadName(){
        var oMsg = $("#com_headMsg");
        var com_hname = $("#com_head").val();

        if (com_hname == "") {
            showErrorMsg(oMsg,"필수 정보입니다.");
            return false;
        }

        hideMsg(oMsg);
        return true;
    }

    function isValidPasswd(str) {
        var cnt = 0;
        if (str == "") {
            return false;
        }

        if (str.length < 8) {
            return false;
        }

        var isPW = /^[a-z0-9][a-z0-9]{7,15}$/;
        if (!isPW.test(str)) {
            return false;
        }

        return true;
    }

    function checkcomId(event){
        if(cidFlag) return true;

        var com_num = $("#com_num").val();
        var oMsg = $("#cidMsg");

        if ( com_num == "" ){
            showErrorMsg(oMsg, "필수 정보입니다")
            return false;
        }

        var isId = /^[0-9][0-9]{9}$/;
        if (!isId.test(com_num)){
            showErrorMsg(oMsg, "10자의 숫자만 입력해주세요.");
            return false;
        }

        cidFlag = false;
        $.ajax({
            type: "post",
            url: "/com_num_check",
            data : {'com_num': com_num },
            dataType: "json",
            success : function(response){
                    if (response.com_ck_val == 0){
                        if (event =="first"){
                            showSuccessMsg(oMsg, "사용할 수 있는 번호입니다.")
                        }else{
                            hideMsg(oMsg);
                        }
                        idFlag = true;
                    } else {
                           showErrorMsg(oMsg, "이미 등록된 번호입니다.");
                    }
            },
            error : function(request, status, error){
                            console.log("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error.status);
                        }
        });
        return true;

    }

    function checkEmail(){
        var email = $("#email").val();
        var oMsg = $("#emailMsg");

        if (email == "") {
            showErrorMsg(oMsg,"필수 정보입니다.");
            return true;
        }

        var isEmail = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        var isHan = /[ㄱ-ㅎ가-힣]/g;
        if (!isEmail.test(email) || isHan.test(email)) {
            showErrorMsg(oMsg,"이메일을 정확히 입력해주세요");
            $("#email").css("background-color", "#FFCECE");
            return false;
        }

        $("#email").css("background-color", "#f9f9ff");
        hideMsg(oMsg);
        return true;

    };


    var isShift = false;
    function checkShiftUp(e) {
        if (e.which && e.which == 16) {
            isShift = false;
        }
    }

    function checkShiftDown(e) {
        if (e.which && e.which == 16) {
            isShift = true;
        }
    }

    function checkCapslock(e) {
        var myKeyCode = 0;
        var myShiftKey = false;
        if (window.event) { // IE
            myKeyCode = e.keyCode;
            myShiftKey = e.shiftKey;
        } else if (e.which) { // netscape ff opera
            myKeyCode = e.which;
            myShiftKey = isShift;
        }

        var oMsg = $("#pswd1Msg");
        if ((myKeyCode >= 65 && myKeyCode <= 90) && !myShiftKey) {
            showErrorMsg(oMsg,"Caps Lock이 켜져 있습니다.");
        } else if ((myKeyCode >= 97 && myKeyCode <= 122) && myShiftKey) {
            showErrorMsg(oMsg,"Caps Lock이 켜져 있습니다.");
        } else {
            hideMsg(oMsg);
        }
    }


    function submitClose() {
        $("#btnJoin").attr("disabled",true);
    }

    function submitOpen() {
        $("#btnJoin").attr("disabled",false);
    }

    function defaultScript() {
            $('.input_box').click(function() {
                $(this).children('input').focus();
                $(this).addClass('focus');
            }).focusout(function() {
                var welInputText = $('.input_box');
                welInputText.removeClass('focus');
            });
    }


    function showErrorMsg(obj, msg) {
            obj.attr("class", "error_next_box");
            obj.html(msg);
            obj.show();
    }


    function showSuccessMsg(obj, msg) {
            obj.attr("class", "error_next_box green");
            obj.html(msg);
            obj.show();
    }


    function hideMsg(obj) {
            obj.hide();
    }

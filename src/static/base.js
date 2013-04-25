    $(document).ready(function(){
    	//添加table行
        $("#table1 #addtr").bind('click', function(){
            $("#tbody1").append(
            	'<tr>' + $('#tbody1 tr:first-child').html() + '</tr>'
            );
        });
        $("#tbody1 .icon-remove").bind('click', function(){
            //$(this).parents('tr').remove();//？？？？？？
        });
        //是否显示基本信息层
        $("#basedivmsg").click(function(){
            var str=$("#baseinfo").css("display");
            if (str == "none") {
                $("#baseinfo").show();
                $("#basedivmsg").html("隐藏基本信息");
            } else {
                $("#baseinfo").hide();
                $("#basedivmsg").html("显示基本信息");
            }  
        });
        
        
        
    });
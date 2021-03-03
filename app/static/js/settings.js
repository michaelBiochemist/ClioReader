function  doWrongSubmit() {
        var form = $('#passwordreset');
        //var formMessages = $("#form-messages");
        var formData = $(form).serialize();
	var response;
        $.ajax ({
                type: 'POST',
                url: '/update_password',
                data: formData
        }) .done(function(response) {
                /*var inputs = document.getElementsByTagName("input");*/
                console.log(response);
		var output = document.getElementById("output");
		output.innerHTML=response;
		/*
                if (response.slice(response.length-13)=="successfully!") {
                        for (i=0; i < inputs.length; i++) {
                                if (inputs[i].type == "text") {
                                        inputs[i].value="";
                                }
                        }
                }*/
        }) .fail(function(data) {
		var output = document.getElementById("output");
		output.innerHTML=data.text;
                /*$(formMessages).removeClass('success');
                $(formMessages).addClass('error');
                if (data.responseText !== '') {
                        $(formMessages).text(data.responseText);
                } else {
                        $(formMessages).text("An error has occurred for some unknown reason, but don't worry: it was probably your fault.");
                }*/
		console.log(response);
                
        });
}
function  doAjaxSubmit() {
        var form = $('#passwordreset');
        var formMessages = $("#output");
        var formData = $(form).serialize();
	console.log(formData);
        $.ajax ({
                type: 'POST',
                url: '/update_password',
                data: formData
        }) .done(function(response) {
                $(formMessages).removeClass('error');
                $(formMessages).addClass('success');
                $(formMessages).text(response);
                var inputs = document.getElementsByTagName("input");
                console.log(response.slice(response.length-13));
                if (response.slice(response.length-13)=="successfully!") {
                        for (i=0; i < inputs.length; i++) {
                                if (inputs[i].type == "text") {
                                        inputs[i].value="";
                                }
                        }
                }
        }) .fail(function(data) {
                $(formMessages).removeClass('success');
                $(formMessages).addClass('error');
                if (data.responseText !== '') {
                        $(formMessages).text(data.responseText);
                } else {
                        $(formMessages).text("An error has occurred for some unknown reason, but don't worry: it was probably your fault.");
                }
                
        });
}


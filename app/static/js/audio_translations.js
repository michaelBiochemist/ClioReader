function update_price(bookid) {
	console.log("updating price");
	var price = Number(document.getElementById("Price|" + bookid).innerHTML);
	var add_sub = document.getElementById("WillPurchase|" + bookid).checked;
	//console.log(add_sub);
	//price == double(price);
	if (add_sub == false) {
		price*=-1;	
	}
	var price_sum = document.getElementById("price_sum");
	price_sum.innerHTML = Number(price_sum.innerHTML) + price;
	document.getElementById("paypalPrice").value == price_sum.innerHTML;
};
function recalculate_price() {
	console.log("re-calculating price.");
	var tbody = document.getElementById("audioproject_table");
	var sum = 0.25;
	var uid = document.getElementById('uid').innerHTML;
	var items = document.getElementById('paypal_custom_message');
	items.value = uid + "|"
	//console.log(tbody.rows);
	for (var i=1; i < tbody.rows.length; i++) {
		//[2]? is price and 3 is whether to buy?
		//console.log(i);
		//console.log(tbody.rows[i].cells[3].children[0].checked);
		if(tbody.rows[i].cells[3].children.length == 1) {
			if (tbody.rows[i].cells[3].children[0].checked == true) {
				sum+=Number(tbody.rows[i].cells[2].innerHTML);
				items.value+=tbody.rows[i].id;
				console.log(tbody.rows[i].cells[0].innerHTML);
				console.log(items);
			}
		}
	}
	var ppalP = document.getElementById("paypalPrice");
	var ppalP2 = document.getElementById("paypalPrice2");
	var priceSum = document.getElementById("price_sum");
	ppalP.value = sum;
	ppalP2.value = sum;
	priceSum.innerHTML = sum;
};
function  doAjaxSubmit() {
        var form = $('#paypal_form');
        //var formMessages = $("#form-messages");
        var formData = $(form).serialize();
	var response;
        $.ajax ({
                type: 'POST',
                url: '/buy_books',
                data: formData
        }) .done(function(response) {
                /*$(formMessages).removeClass('error');
                $(formMessages).addClass('success');
                $(formMessages).text(response);
                var inputs = document.getElementsByTagName("input");*/
                console.log(response);
		/*
                if (response.slice(response.length-13)=="successfully!") {
                        for (i=0; i < inputs.length; i++) {
                                if (inputs[i].type == "text") {
                                        inputs[i].value="";
                                }
                        }
                }*/
        }) .fail(function(data) {
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


function buy_stuff() {
	recalculate_price();
	console.log('Submitting Ajax Request');
	doAjaxSubmit();
	console.log('Submitting Form');
	var x = document.getElementById('paypal_form');
	console.log(x.form);
	x.action();
	//document.forms["paypal_form"].submit();
}

//Call Pre-Load functions

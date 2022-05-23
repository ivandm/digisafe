$(document).ready(function() {

    var asyncSuccessMessage = " "

    function choosePriceModalForm() {
      $("#modal-list").each(function () {
        $(this).modalForm({
          formURL: "{% url 'pricelist:modal-list' %}?session_id={{object.id}}",
          asyncUpdate: true,
          asyncSettings: {
            closeOnSubmit: true,
            successMessage: asyncSuccessMessage,
            dataUrl: "{% url 'pricelist:modal-getprice' %}?session_id={{object.id}}",
            dataElementId: "#price-table",
            dataKey: "table",
            addModalFormFunction: reinstantiateFunction
          }
        });
      });
    }

    async function updatePriceSession(){
//        console.log("updatePriceSession")
        var url = `{% url 'pricelist:modal-getprice' %}?session_id={{object.id}}`;
        // Update page without refresh
            $.ajax({
                type: "GET",
                url:url,
                dataType: "json",
                success: function (response) {
                    // Update page
                    $("#price-table").html(response["table"]);
                    }
            });
    }

    function reinstantiateFunction(){
        //updatePriceSession();
        choosePriceModalForm();
    }
    updatePriceSession();
    reinstantiateFunction();
})
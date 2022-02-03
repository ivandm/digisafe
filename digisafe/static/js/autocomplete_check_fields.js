'use strict';
window.addEventListener("load", function() {
    (function($) {
        console.log('page is fully loaded');
        var obj = $('input[autocomplete_check=autocomplete_check_field]');
        $('input[autocomplete_check=autocomplete_check_field]').each(function(){
            var obj = $(this);
            var id  = obj.attr("id");
            obj.parent().parent().append("<div class='form-row'' id='target_"+id+"'></div>");
        });
        
        $('input[autocomplete_check=autocomplete_check_field]').on("input", function() {
            var obj = $(this);
            
            var id = obj.attr("id");
            var term = obj.val();
            var model_name = obj.attr("autocomplete_check_model_name");
            var app_label  = obj.attr("autocomplete_check_app_label");
            var field_name = obj.attr("autocomplete_check_field_name");
            // console.log(term);
            var url = "/admin/autocomplete_check_field/";
            var data = {
                        "term": term,
                        "model_name": model_name,
                        "app_label": app_label,
                        "field_name": field_name,
                    }
            $.ajax({
              url: url,
              data: data,
            }).done(function( data ) {
                // console.log( '#target_'+id );
                var results = data["results"][0]
                // console.log( results );
                // console.log( results.length );
                if (results !== null){
                    var html = "";
                    for (let i = 0; i < results.length; i++) {
                      html = html + "<div class='form-row'>"+results[i]["text"]+"</div>";
                    }
                    // console.log( html );
                    $('#target_'+id).html(html); 
                }else{
                    $('#target_'+id).html(""); 
                }
                
            });
        });        
    })(django.jQuery);
});

function change_input(e){
    
};
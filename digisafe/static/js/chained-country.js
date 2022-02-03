'use strict';
function getCities(obj) {
    let $ = django.jQuery;
    var obj_set_id = obj.name.replace("-country", "");
    var country_id = obj.value;
    $.get('/countries/country/' + country_id, function (resp){
        let cities_list = '<option value="" selected="">---------</option>'
        $.each(resp.data, function(i, item){
           cities_list += '<option value="'+ item.id +'">'+ item.name +' ('+ item.prov +')</option>'
        });
        $('#id_city[name="'+obj_set_id+'-city"]').html(cities_list);
    });
}
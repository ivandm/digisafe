{% load i18n static %}

// todo: implementazione nella mappa della ricerca markers per jobs come dal companies.model sessionbook.jobs
/* MANAGE MAP AND CHARTBAR */

/* Global declarations */


/* Map functions */
/* Maps declarations TILES */
const copy = "© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors";
//const url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
const osm = L.tileLayer(url, { attribution: "IRCoT" });
const satellite = L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
});
const terrain = L.tileLayer('http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',{
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
});
const map = L.map("map");
osm.addTo(map);

/* MAP lAYER GROUP */
var layercluster = L.markerClusterGroup().addTo(map);
const layerNormalMarkers = layercluster;
const layerFavoriteMarkers = layercluster;
//var layerNormalMarkers = L.layerGroup().addTo(map);
//var layerFavoriteMarkers = L.layerGroup().addTo(map);

/* MAP LAYER CONTROLS */
var baseMaps = {
    "Streets": osm,
    "Satellite": satellite,
    "Terrain": terrain,
};
var overlayMaps = {
    //"Normal": layerNormalMarkers,
    //"Favorite": layerFavoriteMarkers,
};

//const map = L.map("map", { layers: [osm, layerNormalMarkers, layerFavoriteMarkers] });

var layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map);
map.addControl(L.control.search({ position: 'topleft' }));

/* MAP MARKERS const declarations */
var normal_markers = 0,
    favorite_markers = 0,
    location_search = "",
    total_users_map = {}
    ;

/* Map device position request */
map.
    locate()
    .on("locationfound", (e) => map.setView(e.latlng, 8))
    .on("locationerror", () => map.setView([41.9027835,12.4963655], 8));

/* MAP EVENT */
map.on("moveend", render_markers);

/* Manage markers */
/* Load markers */
async function load_markers( url, favorite=false ) {
    const qs = $("input#job_input").val();
    const d_in = $("input#date_in_input").val();
    const d_out = $("input#date_out_input").val();
    const days = $("input#days_input").val();
    const busy = $("input#busy_input").is(":checked");
    const query_str = `in_bbox=${map.getBounds().toBBoxString()}&search=${qs}&date_in=${d_in}&date_out=${d_out}&favorite=${favorite}&days=${days}&busy=${busy}`;
    const markers_url = `${url}?${query_str}`;
    const response = await fetch(markers_url);
    //console.log("response", response);
    const geojson = await response.json();
    //console.log("geojson", geojson);
    return geojson;
}

/* Add markers to map */
function addMarkers(layer, markers, icon_url){
    var num_markers = 0;
    L.geoJSON(markers, {
        pointToLayer: function(feature, latlng) {
            num_markers ++;
            var smallIcon = new L.Icon({
                 iconSize: [32, 32],
                 iconAnchor: [13, 27],
                 popupAnchor:  [1, -24],
                 iconUrl: icon_url
             });
            return L.marker(latlng, {icon: smallIcon});
        },
        onEachFeature: function (feature, layer) {
            //console.log("user_id: ", feature.properties.user_id);
            total_users_map[`${feature.properties.user_id}`] = feature.properties.user_id;
            var tooltip = feature.properties.marker_info;
            tooltip = tooltip + `
            <div class="text-center fs-6">
                <button onclick='favorite_user(this)'
                user_id='${feature.properties.user_id}' class='btn btn-danger bi-heart-half'
                data-bs-toggle="tooltip" data-bs-placement="top" title="User's Add/Remove to favorite"></button>
                <button onclick='option_list(this)'
                user_id='${feature.properties.user_id}' class='btn btn-info bi-list-task'
                data-bs-toggle="tooltip" data-bs-placement="top" title="User's Add/Remove to option list"></button>
            </div>
            `;
            layer.bindPopup(tooltip);
        }
    })
    .addTo(layer);
    return num_markers;
}

/* Manage markers. Load request, add to map , sync Bar chart etc. */
async function render_markers() {
    $("div#search_div").find("*").attr("disabled", "disabled");
    //$("div#map").find("*").off("click");
    $("div#spinner").show();
    var normal_markers=0, favorite_markers=0;

    /* Clean layers */
    layerNormalMarkers.clearLayers();
    layerFavoriteMarkers.clearLayers();

    /* Default position markers */
    var url = "{{api_markers_defaultposition_url}}";
    var markers = await load_markers(url);
    var icon_url = '{% static "imgs/icons/marker_home.png" %}';
    normal_markers += addMarkers(layerNormalMarkers, markers, icon_url);
    addRowsFromDefaultPosition(markers); //CHART

    markers = await load_markers(url, favorite=true);
    var icon_url = '{% static "imgs/icons/marker_home_favorite.png" %}';
    favorite_markers += addMarkers(layerFavoriteMarkers, markers, icon_url);
    addRowsFromDefaultPosition(markers); //CHART

    /* Free position markers */
    var url = "{{api_markers_agenda_url}}";
    var markers = await load_markers(url);
    var icon_url = '{% static "imgs/icons/marker_free.png" %}';
    normal_markers += addMarkers(layerNormalMarkers, markers, icon_url);
    addRows(markers); //CHART

    markers = await load_markers(url, favorite=true);
    var icon_url = '{% static "imgs/icons/marker_free_favorite.png" %}';
    favorite_markers += addMarkers(layerFavoriteMarkers, markers, icon_url);
    addRows(markers); //CHART

    /* Busy position markers */
    var url = "{{api_markers_agendabusy_url}}";
    var markers = await load_markers(url);
    var icon_url = '{% static "imgs/icons/marker_busy.png" %}';
    normal_markers += addMarkers(layerNormalMarkers, markers, icon_url);
    addRows(markers); //CHART

    markers = await load_markers(url, favorite=true);
    var icon_url = '{% static "imgs/icons/marker_busy_favorite.png" %}';
    favorite_markers += addMarkers(layerFavoriteMarkers, markers, icon_url);
    addRows(markers); //CHART


    /* Display markers numbers */
    $("#result_number_normal").html(normal_markers);
    $("#result_number_favorite").html(favorite_markers);
    $("#result_number").html(normal_markers+favorite_markers);
    $("#total_users_map").html(Object.keys(total_users_map).length);
    $("div#spinner").hide();
    //$("div#map").find("*").on("click");
    chart.clearChart();
    drawChart();
    $("div#search_div").find("*").removeAttr("disabled");

}

/* Manage user action. Add/Remove Favorite, Option list etc. */
/* Add/Remove user in SessionBook.user_option_list related field */
async function option_list(e){
    var user_id =  $(e).attr("user_id");
    var url = `{{optionlist_url}}?user_id=${user_id}`;
    const response = await fetch(url);
    const geojson = await response.json();
    retrive_option_list();
}

/* Send invite now */
async function send_invite_now(e){
    var el = e;
    var url = "../invite/";
    const response = await fetch(url);
    const geojson = await response.json();
    if(geojson.send == true){
        console.log("Invio effettuato");
        toastMsg("Invito rapido", "Email inviate");
        $(e).prop( "disabled", true );
        myVar = setTimeout(function(){
            $(el).prop( "disabled", false );
        }, 10*60*1000);
    }
}

/* Return list of user_option_list  */
async function retrive_option_list(){
    el = $("ul#option_list_display");
    var url = `{{retrive_optionlist_url}}?json=true`;
    const response = await fetch(url);
    const geojson = await response.json();
    var html_list_li = "";
    geojson.forEach( function(item, index){
        var tooltip = item.jobs;
        var link_del  = `<a onclick="option_list(this)" user_id="${item.id}">
                        <i class="bi bi-eraser-fill"></i></a>`;
        html_list_li += `<li data-bs-toggle="tooltip" data-bs-placement="left" title="${tooltip}">
                        ${link_del} ${item.user}</li>`;
    });
    el.html(html_list_li);
}

/* Add/Remove user in Company.favorite related field */
async function favorite_user(e){
    var user_id =  $(e).attr("user_id");
    var url = `{{favoriteuser_url}}?user_id=${user_id}`;
    const response = await fetch(url);
    const geojson = await response.json();
}

/* Manage search parameters. Job, Datas, Extra days etc.*/
/* Search job via GET api */
async function search_job(value, url) {
    const search_url = url;
    //console.log(search_url);
    const response = await fetch(search_url)
    const geojson = await response.json()
    return geojson
}

/* Display job searched */
async function set_results(el, display){
    el.attr("url");
    var url = `${el.attr("url")}?qs=${el.val()}`;
    results = await search_job(el.val(), url);
    display.html('');
    results.forEach(function(item, index){
        //console.log(index, item);
        display.append(`<li target_id="${el.attr('id')}" onclick="job_choice(this)" value="${item.id}" >${item.title}</li>`);
    });
}

/* Select job from list display under input field */
function job_choice(e){
    //console.log($(e).attr("value"));
    //console.log($(e).html());
    var target = $(e).attr("target_id"),
        id = $(e).attr("value"),
        title = $(e).html();
    //console.log(target);
    $(`#${target}`).val(title);
    //var div = $("select#job_input");
    var display_result = $(`div#${target}_list_results ul`);
    display_result.html('');
    render_markers();
};

/* EVENTS for Job, Date, Extra Days */
/* job input event for searching job title */
$("input#job_input[event*='onkeyup']").keyup(async function(){
    //console.log($(this).attr("id"));
    var el = $(this);
    var el_id = el.attr("id");
    var el_value = el.val()
    var display_result = $(`div#${el_id}_list_results ul`)
    //console.log(display_result);
    if ( el_value.length > 1){
        //console.log(results);
        await set_results(el, display_result);
    }
});

/* Dates input event */
$("input#date_in_input").change(async function(){
    render_markers();
});

$("input#date_out_input").change(async function(){
    render_markers();
});

/* Days input event */
$("input#days_input").change(async function(){
    render_markers();
});

/* CHART BAR TIMELINE */
var rowsDatas = [];
var colors = [];
var chart;                  // chart representation

/* Google API loading */
google.charts.load('current', {'packages':['timeline']});
google.charts.setOnLoadCallback(drawChart);

/* Draw chart */
function drawChart() {
    var container = document.getElementById('timeline');
    chart = new google.visualization.Timeline(container);
    var dataTable = new google.visualization.DataTable();

    dataTable.addColumn({ type: 'string', id: 'User' });
    dataTable.addColumn({ type: 'string', id: 'Name' });
    dataTable.addColumn({ type: 'string',  id: 'style', role: 'style' });
    dataTable.addColumn({ type: 'string',  role: 'tooltip' });
    dataTable.addColumn({ type: 'date', id: 'Start' });
    dataTable.addColumn({ type: 'date', id: 'End' });

    var Rows = [
        ["Range","Search date range", "ligthblue", "", new Date($("input#date_in_input").val()+" 00:01"),new Date($("input#date_out_input").val()+" 23:59")]
      ];

    dataTable.addRows(Rows.concat(rowsDatas));
    var options = {
      alternatingRowStyle: true,
      //avoidOverlappingGridLines: false,
      backgroundColor: '#ffd',
      height: 400,
      timeline: {
        colorByRowLabel: true,
      }
    };
    chart.draw(dataTable, options);
    //chart.clearChart();
    rowsDatas = [];
}

/* Add datas to Chart from Agenda */
const   color_busy = "black",
        color_free = "green",
        color_def_pos = "yellow",
        color_def_busy = "#595959",
        color_def_free = "#00b300";

function addRows(markers){
    //console.log(markers);
    //console.log(markers.features);
    markers.features.forEach(function(item, index){
        //console.log(item.properties.user, item.properties.tooltip, );
        //console.log(new Date(item.properties.date_end));
        var tooltip =
            `<div class="card" style="width: 18rem;">
              <div class="card-body">
                User's Agenda Position
                <h5 class="card-title">${item.properties.tooltip}</h5>
                <p class="card-text">Is <span class="fw-bold fst-italic">${item.properties.busy_free}</span></p>
                <p class="card-text">From <b>${item.properties.date_start}</b> to <b>${item.properties.date_end}</b></p>
              </div>
            </div>`;
        if(item.properties.busy){
            var color = color_busy;
        }else{
            var color = color_free;
        }
        //console.log(new Date(`${item.properties.date_start} 00:01`));
        rowsDatas.push.apply(rowsDatas, [[
            item.properties.user,
            item.properties.busy_free,
            color,
            tooltip,
            new Date(`${item.properties.date_start} 00:01`),
            new Date(`${item.properties.date_end} 23:59`)
        ]])

    })
}

/* Check point inside coordinates map box */
function inside_map_box(pnt){
    let pattern = /-?\d+\.\d+/g;
    [lon, lat] = pnt.split(";")[1].match(pattern);;
    var latlng = L.latLng(lat, lon);
    return map.getBounds().contains(latlng)
 }

/* Add datas to Chart from Default position */
function addRowsFromDefaultPosition(markers){
    //console.log(markers);
    //console.log(markers.features);

    markers.features.forEach(function(item, index){
        //console.log(item.properties.user, item.properties.tooltip, );
        //console.log(item.properties.user);
        //console.log(JSON.parse(item.properties.agenda));
        var agenda = JSON.parse(item.properties.agenda);
        var agenda_datas = [];
        /* Inserisce gli impegni in agenda */
        //console.log(map.getBounds());

        agenda.forEach(function (agendaitem, index){
            //console.log(agendaitem.fields.city);
            pnt = agendaitem.fields.city;
            if(agendaitem.fields.busy){
                var color = color_def_busy;
                var label = "Agenda Busy";

            }else{
                var color = color_def_free;
                var label = "Agenda Free";
            }
            if( inside_map_box(pnt) ){
                var in_map  = " inside map";
            }else{
                var in_map  = " outside map";
            }
            var d_start = new Date(`${agendaitem.fields.date_start}`);
            var d_end = new Date(`${agendaitem.fields.date_end}`);
            var d_start_display = `${d_start.getDate()}-${d_start.getMonth()+1}-${d_start.getFullYear()}`;
            var d_end_display = `${d_end.getDate()}-${d_end.getMonth()+1}-${d_end.getFullYear()}`;
            agenda_datas.push.apply(agenda_datas, [[
                                        d_start_display,
                                        d_end_display
                                    ]]);
            var tooltip =
                `<div class="card" style="width: 18rem;">
                  <div class="card-body">
                    User's Default Position
                    <h5 class="card-title">${item.properties.tooltip}</h5>
                    <p class="card-text"><b>${in_map.toUpperCase()}</b></p>
                    <p class="card-text">From <b>${d_start_display}</b> to <b>${d_end_display}</b></p>
                  </div>
                </div>`;
            rowsDatas.push.apply(rowsDatas, [[
                item.properties.user,
                label+in_map,
                color,
                tooltip,
                d_start,
                d_end
            ]])
        });

        /* Inserisce la posizione di Default se visualizzato nella mappa */
        //console.log("No Agenda Items");
        var d_start = new Date( $("input#date_in_input").val()  + " 00:01");
        var d_end   = new Date( $("input#date_out_input").val() + " 23:59");
        var d_start_display = `${d_start.getDate()}-${d_start.getMonth()+1}-${d_start.getFullYear()}`;
        var d_end_display = `${d_end.getDate()}-${d_end.getMonth()+1}-${d_end.getFullYear()}`;

        var out_datas = "";
        agenda_datas.forEach(function (dataitem, index){
            out_datas = out_datas + `<p>From ${dataitem[0]} to ${dataitem[1]}</p>`;
        });
        var tooltip =
            `<div class="card" style="width: 18rem;">
              <div class="card-body">
                User's Default Position
                <h5 class="card-title">${item.properties.tooltip}</h5>
                <p class="card-text">From <b>${d_start_display}</b> to <b>${d_end_display}</b></p>
                Ad esclusione delle seguenti date:
                ${out_datas}
              </div>
            </div>`;
        rowsDatas.push.apply(rowsDatas, [[
            item.properties.user,
            "Default position",
            color_def_pos,
            tooltip,
            d_start,
            d_end
        ]]);
        //console.log(rowsDatas);

    })
}

const toastLiveMsg = document.getElementById('liveToastMsg');
const liveToastMsg_head = $("#liveToastMsg_head");
const liveToastMsg_body = $("#liveToastMsg_body");
function toastMsg(head, body) {
    liveToastMsg_head.html(head);
    liveToastMsg_body.html(body);
    var toast = new bootstrap.Toast(toastLiveMsg)
    toast.show()
}

/* Initial Trigger */
retrive_option_list(); //inizializza la lista utenti all'apertura della pagina
//render_markers();
//console.log("end map.js")

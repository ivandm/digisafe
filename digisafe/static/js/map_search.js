var map,
    choosenArray,
    userMarker,
    collection,
    init_position,
    url_save_position,
    csrfmiddlewaretoken,
    viewSaveButton;

function addr_search()
{
    var inp = document.getElementById("addr");
    var xmlhttp = new XMLHttpRequest();
    var url = "https://nominatim.openstreetmap.org/search?format=json&limit=3&q=" + inp.value;
    xmlhttp.onreadystatechange = function()
    {
        if (this.readyState == 4 && this.status == 200)
            {
                var myArr = JSON.parse(this.responseText);
                choosenArray = myArr;
                viewSearch(myArr);
            }
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

function viewSearch(arr)
{
    var out = "<br />";
    var i;

    if(arr.length > 0)
    {
        for(i = 0; i < arr.length; i++)
            {
                out += "<div class='address' title='Center hear' onclick='chooseAddr(" + i +");return false;'>" + arr[i].display_name + "</div>";
            }
            document.getElementById('results').innerHTML = out;
        }
    else
    {
        document.getElementById('results').innerHTML = "Sorry, no results...";
    }
}

function chooseAddr(i)
{
    var lat1 = choosenArray[i].lat,
        lng1 = choosenArray[i].lon,
        name = choosenArray[i].display_name;
    map.setView([lat1, lng1],10);
    document.getElementById('select_center').innerHTML = name;
    var myIcon = L.divIcon({className: 'bi-bullseye leaflet-center-icon'});
    var latlng = L.latLng(lat1, lng1);
    centerMarker.setLatLng(latlng);
    if(viewSaveButton){
        saveButton.style.display = "block";
    }

}

function savePositionFunc(){
    var lat = centerMarker.getLatLng().lat;
    var lon = centerMarker.getLatLng().lng;
//    console.log(centerMarker.getLatLng().toString());
    data={
      'csrfmiddlewaretoken':csrfmiddlewaretoken,
      'lat':lat,
      'lon':lon,
      };
    $.ajax({
        url: url_save_position,
        cache:'false',
        dataType:'json',
        type:'POST',
        data:data,
        success: function(data){
           //do something
//           console.log(data);
        },
        error: function(error){
          alert('error; '+ eval(error));
        }
    });
}

function setNewMarker(latlng){
//    console.log(latlng);
    centerMarker.setLatLng(latlng);
    if(viewSaveButton){
        saveButton.style.display = "block";
    }

}

function eventClickMap(e){
    setNewMarker(e.latlng);
    eventDraggedMarker();
}

function eventDraggedMarker(e){
    var lat = centerMarker.getLatLng().lat;
    var lon = centerMarker.getLatLng().lng;
    map.setView([lat, lon]);
    var latlng = L.latLng(lat, lon);
    setNewMarker(latlng);
    var xmlhttp = new XMLHttpRequest();
    var url = "https://nominatim.openstreetmap.org/reverse?lat="+lat+"&lon="+lon+"&format=jsonv2";
    xmlhttp.onreadystatechange = function()
    {
        if (this.readyState == 4 && this.status == 200)
            {
//                console.log(this.responseText);
                var myArr = JSON.parse(this.responseText);
                var name = myArr.display_name;
                document.getElementById('select_center').innerHTML = name;
//                var myArr = JSON.parse(this.responseText);
//                choosenArray = myArr;
//                viewSearch(myArr);

            }
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

function onEachFeature(feature, layer)
{
    if (feature.properties && feature.properties.popupContent) {
      layer.bindPopup(feature.properties.popupContent);
    }
}

function map_init(mymap, options)
{
//    console.log("map_init");
    map = mymap;
    var myIcon = L.divIcon({className: 'bi-bullseye leaflet-center-icon'});
    var lat = 0, lon = 0;
    if(init_position){
        var lat = init_position[1];
        var lon = init_position[0];
        map.setView([lat, lon]);
    }
    saveButton = document.getElementById('savePosition');
    centerMarker = new L.marker([lat,lon], {draggable: true});
    centerMarker.setIcon(myIcon);
    centerMarker.addTo(map);
    centerMarker.on('dragend', function(e){
//        console.log(e);
        eventDraggedMarker(e);
    });

    map.on('click', function(e){
        eventClickMap(e);
    });

    if(collection){
        L.geoJson(collection, {onEachFeature: onEachFeature}).addTo(map);
    }

}
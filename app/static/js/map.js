var markers = {}

$(document).ready(function () {

    // Initialize world map and center it to the user position
    var map = L.map('map');

    L.tileLayer('//api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18,
        id: MAPBOX_ID,
        accessToken: MAPBOX_TOKEN
    }).addTo(map);

    map.locate({setView: true, maxZoom: 5});

    map.on('locationfound', onLocationFound);

    // Assign a fingerprint to the user
    var fp = $.cookie('fp');

    if (!fp) {
        fp = createFingerprint();
        $.cookie('fp', fp);
    }

    // Create socketIO connection
    var socket = io.connect('//' + document.domain + ':' + location.port);

    // Send user location to the server once he accepts geo location
    function onLocationFound(e) {
        socket.emit('send_pos', e.latlng.lat, e.latlng.lng, e.timestamp, fp);
        // Display user location
        L.marker([e.latlng.lat, e.latlng.lng]).addTo(map).bindPopup("<b>This is you</b>.").openPopup();
    }

    // Handle positions init
    socket.on('init_pos', function (data) {
        refreshPositions(map, data.pos, fp);
    });

    // Handle positions update
    socket.on('update_pos', function (data) {
        refreshPositions(map, data.pos, fp);
    });

});


function createFingerprint() {

    var fingerprint = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });

    return fingerprint;

}

function refreshPositions(map, positions, userFp) {

    for (var i = 0; i < positions.length; i++) {

        position = positions[i];

        if (position.fp in markers) {
            // Refresh the position if it's already on the map
            markers[position.fp].setLatLng(new L.LatLng(position.lat, position.long)).bindPopup('Last seen ' + moment(position.timestamp).fromNow());
        } else if (position.fp != userFp) {
            // Create a marker for the position if it's not the current user position
            markers[position.fp] = L.marker([position.lat, position.long]).addTo(map).bindPopup('Last seen ' + moment(position.timestamp).fromNow());
        }

    }
}
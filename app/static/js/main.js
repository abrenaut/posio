var uuid = null,
    map = null,
    assetLayer = null,
    socket = null;

$(document).ready(function () {

    uuid = createUUID();

    map = createMap();

    assetLayer = createAssetLayer(map);

    socket = createSocket();

    // Handle new turn
    socket.on('new_turn', newTurn);

    // Hanle end of turn
    socket.on('end_of_turn', endTurn);

});

function createUUID() {

    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });

}

function createMap() {

    var map = L.map('map', {
        layers: [
            L.tileLayer('http://stamen-tiles-{s}.a.ssl.fastly.net/toner-background/{z}/{x}/{y}.{ext}', {
                attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                noWrap: true,
                ext: 'png'
            })],
        zoom: 2,
        maxZoom: 2,
        minZoom: 2,
        zoomControl: false,
        center: [49, 2.5],
        maxBounds: [
            [-70.0, -180.0],
            [85.0, 180.0]
        ]

    });

    map.touchZoom.disable();
    map.doubleClickZoom.disable();
    map.scrollWheelZoom.disable();

    $('.leaflet-container').css('cursor', 'crosshair');

    return map;

}

function createAssetLayer(map) {

    return new L.LayerGroup().addTo(map);

}

function createSocket() {

    return io.connect('//' + document.domain + ':' + location.port);

}

function answer(e) {
    // Disable answers for this turn
    map.off('click', answer);
    // Mark the answer on the map
    var answerMarker = L.marker(e.latlng).addTo(map);
    assetLayer.addLayer(answerMarker);
    // Emit answer event
    socket.emit('answer', uuid, e.latlng.lat, e.latlng.lng);
}

function newTurn(data) {
    // Update game rules
    $('#game_rules').html('Locate ' + data.city + ' (' + data.country + ')<div id="progress" class="progress"></div>');
    // Show countdown timer
    showCountdownTimer('#progress', ANSWER_DURATION);
    // Clear potential markers from previous turn
    assetLayer.clearLayers();
    // Enable answers for this turn
    map.on('click', answer);
}

function endTurn(data) {
    // Disable answers
    map.off('click', answer);
    // If user has answered, show result
    if (uuid in data.answers) {
        var userAnswer = data.answers[uuid];
        var resultText = 'You are ' + distance(data.correct.lat, data.correct.lng, userAnswer.lat, userAnswer.lng) + ' km away<br/>';
        /*resultText += 'You are #';*/
        $('#game_rules').html(resultText);

        // Show correct location on the map
        var correctAnswerMarker = L.marker([data.correct.lat, data.correct.lng]).addTo(map);
        assetLayer.addLayer(correctAnswerMarker);
    } else {

        $('#game_rules').html('No answer given');

    }
}

function distance(lat1, lon1, lat2, lon2) {
    var radlat1 = Math.PI * lat1 / 180;
    var radlat2 = Math.PI * lat2 / 180;
    var theta = lon1 - lon2;
    var radtheta = Math.PI * theta / 180;
    var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
    dist = Math.acos(dist);
    dist = dist * 180 / Math.PI;
    dist = dist * 60 * 1.1515 * 1.609344;
    return dist;
}

function showCountdownTimer(container, duration) {
    var progressbar = new ProgressBar.Line(container, {
        color: '#FCB03C',
        duration: duration * 1000
    });
    progressbar.animate(1);
}
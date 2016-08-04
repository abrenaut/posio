var uuid = null,
    map = null,
    markerGroup = null,
    socket = null,
    started = false;

$(document).ready(function () {

    // Create a unique ID to identify user answers
    uuid = createUUID();

    // Create the leaflet map
    map = createMap();

    // Create the web socket
    socket = io.connect('//' + document.domain + ':' + location.port);

    // Create the marker group used to clear markers between turns
    markerGroup = new L.LayerGroup().addTo(map);

    // Handle new turn
    socket.on('new_turn', newTurn);

});

function createUUID() {

    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });

}

function createMap() {

    // Create a world map
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
        // Force the user to stay between the given bounds
        maxBounds: [
            [-70.0, -180.0],
            [85.0, 180.0]
        ]

    });

    // Disable Zoom
    map.touchZoom.disable();
    map.doubleClickZoom.disable();
    map.scrollWheelZoom.disable();

    $('.leaflet-container').css('cursor', 'crosshair');

    // Add a legend to the map
    var legend = L.control({position: 'bottomleft'});

    legend.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info legend');
        div.innerHTML += '<img height="20" width="12" src="https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png" alt="Your answer"/> Your answer<br>';
        div.innerHTML += '<img height="20" width="12" src="https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png" alt="Correct answer"/> Correct answer<br>';
        div.innerHTML += '<img height="20" width="12" src="https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png" alt="Best answer"/> Closest answer<br>';
        return div;
    };

    legend.addTo(map);

    return map;

}

function newTurn(data) {

    // Update the started flag
    started = true;

    // Clear potential markers from previous turn
    markerGroup.clearLayers();

    // Update game rules to show the city to find
    $('#game_rules').html('Locate <span class="city">' + data.city + '</span> (' + data.country + ')<div id="progress" class="progress"></div>');

    // Show countdown timer
    showCountdownTimer('#progress', ANSWER_DURATION);

    // Enable answers for this turn
    map.on('click', answer);

    // Handle end of turn
    socket.on('end_of_turn', endTurn);

}

function endTurn(data) {

    // Disable answers listener
    map.off('click', answer);

    // Clear markers
    markerGroup.clearLayers();

    // Update game rules
    $('#game_rules').html('Waiting for the next turn');

    // Get rankings and show answers
    var bestAnswer = null;

    // Get the distance between each answer and the city to find
    for (var answerUuid in data.answers) {

        data.answers[answerUuid].distance = distance(data.correct.lat, data.correct.lng, data.answers[answerUuid].lat, data.answers[answerUuid].lng);

        // Update best answer
        bestAnswer = (!bestAnswer || data.answers[answerUuid].distance < bestAnswer.distance) ? data.answers[answerUuid] : bestAnswer;

    }

    // Sort answers in order to get user ranking
    var answersSorted = Object.keys(data.answers).sort(function (a, b) {
        return data.answers[a].distance - data.answers[b].distance
    })

    // Show best answer
    if (bestAnswer) {

        var bestAnswerDistanceRounded = Math.round(bestAnswer.distance * 100) / 100;
        var marker = createMarker(bestAnswer.lat, bestAnswer.lng, 'green');
        addPopup(marker, 'Closest answer (<b>' + bestAnswerDistanceRounded + ' km</b> away)', false);

    }

    // Show correct answer
    var marker = createMarker(data.correct.lat, data.correct.lng, 'red');
    addPopup(marker, data.correct.name, false);

    // Show user answer and ranking
    if (uuid in data.answers) {

        var userDistanceRounded = Math.round(data.answers[uuid].distance * 100) / 100;
        var userRanking = answersSorted.indexOf(uuid) + 1;

        var marker = createMarker(data.answers[uuid].lat, data.answers[uuid].lng, 'blue');
        addPopup(marker, 'Your are <b>#' + userRanking + '</b> out of <b>' + answersSorted.length + '</b> player(s) (<b>' + userDistanceRounded + ' km</b> away)', true);

    }

}

function answer(e) {

    // Disable answers for this turn
    map.off('click', answer);

    // Mark the answer on the map
    createMarker(e.latlng.lat, e.latlng.lng, 'blue');

    // Emit answer event
    socket.emit('answer', uuid, e.latlng.lat, e.latlng.lng);

}

function createMarker(lat, lng, color) {

    var icon = new L.Icon({
        iconUrl: '//cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-' + color + '.png',
        shadowUrl: '//cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconAnchor: [12, 41],
        popupAnchor: [1, -34]
    });

    var marker = L.marker([lat, lng], {icon: icon}).addTo(map);

    markerGroup.addLayer(marker);

    return marker;

}

function addPopup(marker, text, openPopup) {

    var popup = marker.bindPopup(text);

    if (openPopup) {
        popup.openPopup()
    }

}

function showCountdownTimer(container, duration) {

    var progressbar = new ProgressBar.Line(container, {
        color: '#FCB03C',
        duration: duration * 1000
    });

    progressbar.animate(1);

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


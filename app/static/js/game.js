var playerName = 'Arthur',
    map = null,
    markerGroup = null,
    socket = null,
    progressbar = null,
    gameId = 'default';

$(document).ready(function () {

    // Create the leaflet map
    map = createMap();

    // Create the marker group used to clear markers between turns
    markerGroup = new L.LayerGroup().addTo(map);

    // Join the game
    joinGame();

});

function joinGame() {

    // Create the web socket
    socket = io.connect('//' + document.domain + ':' + location.port);

    // Handle new turn
    socket.on('new_turn', handleNewTurn);

    // Handle leaderboard update
    socket.on('leaderboard_update', updateLeaderboard);

    // Join the default game
    socket.emit('join_game', gameId, playerName);

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

function updateLeaderboard(data) {

    $('.score_row').remove();

    for (var i = 0; i < 10; i++) {

        if (data.player_rank == i) {

            $('#leaderboard tr:last').after('<tr class="score_row user_score"><td>' + (i + 1) + '</td><td>You</td><td>' + data.player_score + '</td></tr>');

        } else if(data.top_ten[i]) {

            $('#leaderboard tr:last').after('<tr class="score_row"><td>' + (i + 1) + '</td><td>' + data.top_ten[i].player_name + '</td><td>' + data.top_ten[i].score + '</td></tr>');

        }

    }

}

function handleNewTurn(data) {

    // Clear potential markers from previous turn
    markerGroup.clearLayers();

    // Update game rules to show the city to find
    $('#game_rules').html('Locate <span class="city">' + data.city + '</span> (' + data.country + ')<div id="progress" class="progress"></div>');

    // Show countdown timer
    showCountdownTimer('#progress', ANSWER_DURATION);

    // Enable answers for this turn
    map.on('click', answer);

    // Handle end of turn
    socket.on('end_of_turn', handleEndOfTurn);

    // Handle player results
    socket.on('player_results', showPlayerResults);

}

function handleEndOfTurn(data) {

    // Disable answers listener
    map.off('click', answer);

    // Clear markers
    markerGroup.clearLayers();

    // Show best answer if there is one
    if (data.best_answer) {

        var bestMarker = createMarker(data.best_answer.lat, data.best_answer.lng, 'green');
        bestMarker.bindPopup('Closest answer (<b>' + round(data.best_answer.distance) + ' km</b> away)');

    }

    // Show correct answer
    var correctMarker = createMarker(data.correct_answer.lat, data.correct_answer.lng, 'red');
    correctMarker.bindPopup(data.correct_answer.name);

    // Update game rules
    $('#game_rules').html('Waiting for the next turn');

}

function showPlayerResults(data) {

    var userMarker = createMarker(data.lat, data.lng, 'blue');

    // Show user score, ranking and distance
    var resultsText = '<div class="results"><b>' + round(data.distance) + ' km</b> away: ';

    if (data.score == 0) {
        resultsText += '<span class="score">Too far away!</span>';
    } else {
        resultsText += '<span class="score">+<span id="score_value">0</span> points</span>';
    }

    resultsText += '<br/>Your are <b>#' + data.rank + '</b> out of <b>' + data.total + '</b> player(s)</div>';

    userMarker.bindPopup(resultsText).openPopup();

    if (data.score != 0) {
        // Animate user score
        animateScore(data.score);
    }

}

function answer(e) {

    // Disable answers for this turn
    map.off('click', answer);

    // Mark the answer on the map
    createMarker(e.latlng.lat, e.latlng.lng, 'blue');

    // Emit answer event
    socket.emit('answer', gameId, e.latlng.lat, e.latlng.lng);

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

function showCountdownTimer(container, duration) {

    progressbar = new ProgressBar.Line(container, {
        color: '#FCB03C',
        duration: duration * 1000
    });

    progressbar.animate(1);

}

function round(value) {
    return Math.round(value * 100) / 100
}

function animateScore(score) {
    var duration = 1000;
    // no timer shorter than 50ms (not really visible any way)
    var minTimer = 50;
    // calc step time to show all interediate values
    var stepTime = Math.abs(Math.floor(duration / score));

    // never go below minTimer
    stepTime = Math.max(stepTime, minTimer);

    // get current time and calculate desired end time
    var startTime = new Date().getTime();
    var endTime = startTime + duration;
    var timer;

    function run() {
        var now = new Date().getTime();
        var remaining = Math.max((endTime - now) / duration, 0);
        var value = Math.round(score - (remaining * score));
        $('#score_value').text(value);
        if (value == score) {
            clearInterval(timer);
        }
    }

    timer = setInterval(run, stepTime);
    run();
}

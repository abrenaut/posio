/**
 * Initialize game variables.
 */
let gameStarted = false;

const timeToAnswerQuestion = JSON.parse(
  document.getElementById("time-to-answer-question").textContent
);

const gameContainer = document.getElementById("game-container");

/**
 * Create helper functions.
 */

/**
 * @returns true if user is on a mobile device
 */
const isMobileViewport = () =>
  window.innerWidth <= 560 || window.innerHeight <= 404;

/**
 * Creates a new GeoJSON layer with the given color.
 *
 * @param {*} color the layer color
 * @returns
 */
const createGeoJSONLayer = (color) => {
  return L.geoJSON([], {
    style: (_) => {
      return { fillColor: color, color: color };
    },
    pointToLayer: (_, latlng) => {
      const icon = L.icon({
        iconUrl: document.getElementById(`${color}-marker-icon`).src,
        shadowUrl: document.getElementById("shadow-marker").src,
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
      });
      return L.marker(latlng, { icon: icon });
    },
  });
};

/**
 * Update a GeoJSON layer location.
 * The layer data is retrieved from the input with the given name.
 * If the input is empty, the layer is removed.
 *
 * @param {*} layer
 * @param {*} layerDataInputName
 */
const updateGeoJSONLayerFromInput = (layer, layerDataInputName) => {
  map.removeLayer(layer);
  const locationStr = document.querySelector(
    `input[name="${layerDataInputName}"]`
  ).value;
  if (locationStr) {
    const layerData = JSON.parse(locationStr);
    updateGeoJSONLayer(layer, layerData);
  }
};

/**
 * Update a GeoJSON layer location with the new data.
 *
 * @param {*} layer
 * @param {*} layerData
 */
const updateGeoJSONLayer = (layer, layerData) => {
  layer.clearLayers().addData(layerData);
  map.addLayer(layer);
};

/**
 * Animate the question progress bar.
 */
const animateProgressBar = () => {
  const progressBar = document.querySelector(".progress-bar-fill");
  if (progressBar) {
    // Add a 500ms delay to the animation to account for network latency
    const animationDuration = timeToAnswerQuestion * 1000 - 500;
    progressBar.style.animation = `cssload-width ${animationDuration}ms linear`;
  }
};

/**
 * @returns true if a question is in progress
 */
const isQuestionInProgress = () => {
  const questionInProgressElement = document.querySelector(
    "#question-in-progress"
  );
  return questionInProgressElement.value === "true";
};

/**
 * Animate the player score from 0 to their score in 1 second.
 *
 * @param {*} playerScoreValueElement
 */
const animatePlayerScoreValue = (playerScoreValueElement) => {
  const newValue = parseInt(playerScoreValueElement.textContent);

  // Increase the player score by 5% of the final value every 50ms
  const stepTime = 50;
  const stepOffset = Math.max(Math.abs(Math.floor(newValue / 20)), 1);
  var step = 1;

  const run = () => {
    var value = Math.min(step * stepOffset, newValue);
    playerScoreValueElement.innerHTML = value;

    if (value >= newValue) {
      clearInterval(timer);
    }
    step++;
  };

  const timer = setInterval(run, stepTime);
};

/**
 * Create the map, add the tiles.
 */

const map = L.map("map", {
  // Force the user to stay between the given bounds
  maxBounds: [
    [-85.0, -180.0],
    [85.0, 180.0],
  ],
  // Hide zoom controls
  zoomControl: false,
  doubleClickZoom: false,
});

map.setView([20, 0], 2);

const tiles = L.tileLayer(
  "https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png",
  {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    minZoom: 2,
    maxZoom: 4,
    noWrap: true,
  }
).addTo(map);

/**
 * Create the GeoJSON layers that indicate the correct answer, the top answer
 * and the player's answer.
 * Those layers are initially empty and will be updated when the server sends
 * question / answer  data or the player clicks on the map.
 */

let correctAnswerLayer = createGeoJSONLayer("red");
let topAnswerLayer = createGeoJSONLayer("green");
let playerAnswerLayer = createGeoJSONLayer("blue");

/**
 * Add event listeners:
 * - When the leaderboard header is clicked, toggle the leaderboard table visibility.
 * - When the server sends a message, update the GeoJSON layers.
 */

document.body.addEventListener("click", (evt) => {
  if (evt.target.id !== "leaderboard-header") return;
  document
    .getElementById("leaderboard-table-container")
    .classList.toggle("hidden");
});

document.body.addEventListener("htmx:wsAfterMessage", () => {
  if (isQuestionInProgress()) {
    gameStarted = true;
    // If the user is on a mobile device, reset the map view
    if (isMobileViewport()) {
      map.setView([20, 0], 2);
    }
    animateProgressBar();
  }

  if (gameStarted) {
    // Update the GeoJSON layers with the latest data
    updateGeoJSONLayerFromInput(topAnswerLayer, "top-answer");
    updateGeoJSONLayerFromInput(correctAnswerLayer, "correct-answer");
    updateGeoJSONLayerFromInput(playerAnswerLayer, "player-answer");

    // Show the player's turn result popup
    playerAnswerLayer.unbindPopup();
    const playerMarkerPopupContent = document.querySelector(
      "#player-answer-popup"
    ).innerHTML;
    if (playerMarkerPopupContent) {
      playerAnswerLayer.bindPopup(playerMarkerPopupContent).openPopup();

      // Animate the player score
      const playerScoreValueElement =
        document.getElementById("player-score-value");
      if (playerScoreValueElement) {
        animatePlayerScoreValue(playerScoreValueElement);
      }
    }

    // Show the correct answer tooltip if any
    correctAnswerLayer.unbindTooltip();
    const correctAnswerPopupContent = document.querySelector(
      "#correct-answer-popup"
    ).innerHTML;
    if (correctAnswerPopupContent.trim()) {
      correctAnswerLayer.bindTooltip(correctAnswerPopupContent).openTooltip();
    }

    // If the user is on a mobile device, zoom on the correct answer.
    if (isMobileViewport() && !isQuestionInProgress()) {
      map.fitBounds(correctAnswerLayer.getBounds());
    }
  }
});

map.on("click", (evt) => {
  // If there is no question in progress, do nothing
  if (!isQuestionInProgress()) return;

  // Show the player's answer on the map
  const latitude = evt.latlng.lat;
  const longitude = evt.latlng.lng;

  const layerData = {
    type: "Point",
    coordinates: [longitude, latitude],
  };
  updateGeoJSONLayer(playerAnswerLayer, layerData);

  // Dispatch a custom event with the player's answer
  // so that HTMX can send it to the server
  gameContainer.dispatchEvent(
    new CustomEvent("game:answer", {
      detail: {
        latitude: latitude,
        longitude: longitude,
      },
    })
  );
});

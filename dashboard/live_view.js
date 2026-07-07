// Phase 7/8 -- Live camera view: webcam capture + bounding box overlay

const API_URL = "https://retail-shelf-monitoring.onrender.com/detect_live";
const CAPTURE_INTERVAL_MS = 1500; // send one frame roughly every 1.5s

const video = document.getElementById("webcam");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");
const statusEl = document.getElementById("status");

const countBoxes = {
  "Shelf A": document.getElementById("count-a"),
  "Shelf B": document.getElementById("count-b"),
  "Shelf C": document.getElementById("count-c"),
};

// A hidden canvas used just to grab a snapshot frame from the video
// to send to the backend (separate from the visible overlay canvas)
const captureCanvas = document.createElement("canvas");
const captureCtx = captureCanvas.getContext("2d");

async function startWebcam() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;

    video.addEventListener("loadedmetadata", () => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      captureCanvas.width = video.videoWidth;
      captureCanvas.height = video.videoHeight;

      statusEl.textContent = "Webcam active. Detecting...";
      setInterval(captureAndDetect, CAPTURE_INTERVAL_MS);
    });
  } catch (err) {
    statusEl.textContent = "Could not access webcam: " + err.message;
  }
}

async function captureAndDetect() {
  // Grab the current video frame into the hidden capture canvas
  captureCtx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);

  captureCanvas.toBlob(async (blob) => {
    if (!blob) return;

    const formData = new FormData();
    formData.append("file", blob, "frame.jpg");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        statusEl.textContent = "Detection request failed: " + response.status;
        return;
      }

      const data = await response.json();
      drawDetections(data);
      updateCounts(data.zone_counts || {});
      statusEl.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
    } catch (err) {
      statusEl.textContent = "Error calling detection API: " + err.message;
    }
  }, "image/jpeg", 0.8);
}

function drawDetections(data) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!data.detections) return;

  ctx.strokeStyle = "#00ff88";
  ctx.lineWidth = 2;
  ctx.font = "14px Arial";
  ctx.fillStyle = "#00ff88";

  for (const det of data.detections) {
    const [x1, y1, x2, y2] = det.bbox;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

    if (det.zone) {
      ctx.fillText(det.zone, x1, y1 > 15 ? y1 - 5 : y1 + 15);
    }
  }
}

function updateCounts(zoneCounts) {
  for (const [zoneName, el] of Object.entries(countBoxes)) {
    const count = zoneCounts[zoneName] || 0;
    el.textContent = `${zoneName}: ${count}`;
  }
}

startWebcam();
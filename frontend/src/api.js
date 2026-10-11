
const API_BASE_URL = "http://localhost:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Request failed (${response.status})`);
  }

  return response.json();
}

export function generateQuest(preferences) {
  return request("/quests", {
    method: "POST",
    body: JSON.stringify(preferences),
  });
}

export function saveObservation(missionTitle, observation) {
  return request("/observations", {
    method: "POST",
    body: JSON.stringify({
      mission_title: missionTitle,
      observation,
    }),
  });
}

export function getObservations() {
  return request("/observations");
}

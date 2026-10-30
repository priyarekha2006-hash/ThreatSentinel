const API_BASE_URL = "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch {
    throw new Error(
      "Cannot connect to the backend. Make sure the FastAPI server is running on port 8000."
    );
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || `Request failed: ${response.status}`
    );
  }

  return data;
}

export async function scanText(payload) {
  return request("/api/scan", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getHistory() {
  return request("/api/history");
}

export async function checkHealth() {
  return request("/api/health");
}
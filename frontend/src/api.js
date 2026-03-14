export async function analyzeText(content) {
  const response = await fetch("http://127.0.0.1:9000/api/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ audio_data: "", transcript: content })
  });

  return response.json();
}

export async function analyzeAudio(audioFile) {
  const response = await fetch("http://127.0.0.1:9000/api/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ audio_data: audioFile.name, transcript: "" })
  });

  return await response.json();
}
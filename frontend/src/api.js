export async function analyzeText(content) {

  const response = await fetch("http://127.0.0.1:8000/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ content })
  });

  return response.json();
}


export async function analyzeAudio(file) {

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://127.0.0.1:8000/api/analyze-audio", {
    method: "POST",
    body: formData
  });

  return response.json();
}
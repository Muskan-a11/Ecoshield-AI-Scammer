import React, { useState } from "react";
import { analyzeText, analyzeAudio } from "../api";

export default function ThreatForm({ setResult }) {

  const [text, setText] = useState("");
  const [file, setFile] = useState(null); // state for uploaded file

  const handleTextSubmit = async () => {
    const result = await analyzeText(text);
    setResult(result);
  };

 const handleAudioSubmit = async () => {
  if (!file) {
    alert("Please upload an audio file");
    return;
  }

  const formData = new FormData();
  formData.append("file", file); // key must match FastAPI parameter

  try {
    const response = await fetch("http://127.0.0.1:8000/api/analyze-audio", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Error response:", errorData);
      setResult(errorData);
      return;
    }

    const result = await response.json();
    console.log("Analysis result:", result);
    setResult(result);
  } catch (err) {
    console.error("Network error:", err);
  }
};

  return (
    <div className="card">
      <h2>Analyze Suspicious Message</h2>

      <textarea
        rows="4"
        placeholder="Paste suspicious message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button onClick={handleTextSubmit}>
        Analyze Text
      </button>

      <hr style={{ margin: "30px 0", borderColor: "#222" }} />

      <h2>Upload Call Recording</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])} // <-- set the file state
      />

      <button onClick={handleAudioSubmit}>
        Analyze Audio
      </button>
    </div>
  );
}
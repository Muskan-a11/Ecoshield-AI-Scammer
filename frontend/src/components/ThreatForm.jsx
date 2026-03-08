import { useState } from "react";
import { analyzeThreat } from "../api";

export default function ThreatForm({ setResult }) {

  const [content, setContent] = useState("");
  const [file, setFile] = useState(null);

  // ============================
  // Text Analysis
  // ============================

  const handleAnalyze = async () => {

    if (!content) {
      alert("Please enter some text to analyze.");
      return;
    }

    const data = await analyzeThreat(content);
    setResult(data);
  };

  // ============================
  // Audio Upload Analysis
  // ============================

  const handleAudioUpload = async () => {

    if (!file) {
      alert("Please upload an audio file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://127.0.0.1:8000/api/analyze-audio", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div>

      <h2>Text Scam Detection</h2>

      <textarea
        placeholder="Paste suspicious message or conversation..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />

      <br />

      <button onClick={handleAnalyze}>
        Analyze Text
      </button>


      <hr style={{ margin: "30px 0" }} />


      <h2>Call Recording Detection</h2>

      <input
        type="file"
        accept="audio/*"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br />

      <button onClick={handleAudioUpload}>
        Upload Call Recording
      </button>

    </div>
  );
}
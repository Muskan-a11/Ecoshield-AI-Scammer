import React, { useState } from "react";
import { analyzeText, analyzeAudio } from "../api";

export default function ThreatForm({ setResult }) {

  const [text, setText] = useState("");
  const [file, setFile] = useState(null);

  const handleTextSubmit = async () => {
    const result = await analyzeText(text);
    setResult(result);
  };

  const handleAudioSubmit = async () => {
    const result = await analyzeAudio(file);
    setResult(result);
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

      <hr style={{margin:"25px 0", borderColor:"#222"}}/>

      <h2>Upload Call Recording</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={handleAudioSubmit}>
        Analyze Audio
      </button>

    </div>
  );
}
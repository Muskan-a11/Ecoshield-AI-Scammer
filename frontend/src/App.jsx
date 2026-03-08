import React, { useState } from "react";
import ThreatForm from "./components/ThreatForm";
import ResultCard from "./components/ResultCard";

function App() {

  const [result, setResult] = useState(null);

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>

      <h1>EchoShield AI</h1>
      <p>Detect scam messages and calls using AI</p>

      <ThreatForm setResult={setResult} />

      <ResultCard result={result} />

    </div>
  );
}

export default App;
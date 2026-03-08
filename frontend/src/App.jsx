import React, { useState } from "react";
import ThreatForm from "./components/ThreatForm";
import ResultCard from "./components/ResultCard";

function App() {

  const [result, setResult] = useState(null);

  return (
    <div className="container">

      <div className="header">
        <h1 className="title">EchoShield AI</h1>
        <p className="subtitle">
          AI Powered Scam Message & Call Detection
        </p>
      </div>

      <ThreatForm setResult={setResult} />

      <ResultCard result={result} />

    </div>
  );
}

export default App;
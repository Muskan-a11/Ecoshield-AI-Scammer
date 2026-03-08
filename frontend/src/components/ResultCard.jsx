import React from "react";

export default function ResultCard({ result }) {

  if (!result) return null;

  const analysis = result.analysis ? result.analysis : result;

  return (
    <div style={{ marginTop: "30px" }}>

      {result.transcript && (
        <>
          <h3>Transcript</h3>
          <p>{result.transcript}</p>
        </>
      )}

      <h3>Threat Analysis</h3>

      <p>Deepfake Score: {analysis.deepfake_score}</p>
      <p>Sentiment Score: {analysis.sentiment_score}</p>
      <p>Threat Level: {analysis.threat_level}</p>

      <h2>
        Confidence: {analysis.confidence}%
      </h2>

    </div>
  );
}
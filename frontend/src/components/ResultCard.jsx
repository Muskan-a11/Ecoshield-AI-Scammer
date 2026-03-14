import React from "react";

export default function ResultCard({ result }) {

  if (!result) return null;

  return (
    <div style={{ marginTop: "30px" }}>

      {result.transcript && (
        <>
          <h3>Transcript</h3>
          <p>{result.transcript}</p>
        </>
      )}

      {result.overall_threat_assessment && (
        <>
          <h3>Threat Analysis</h3>

          <p>Deepfake Score: {result.deepfake_detection?.confidence ?? 0}</p>
          <p>Sentiment Score: {result.urgency_detection?.urgency_score ?? 0}</p>
          <p>Threat Level: {result.overall_threat_assessment?.threat_level}</p>

          <h2>
            Confidence: {result.overall_threat_assessment?.combined_confidence * 100}%
          </h2>
        </>
      )}

    </div>
  );
}
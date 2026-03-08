export default function ResultCard({ result }) {

  if (!result) return null;

  // Check if result came from audio endpoint
  const analysis = result.analysis ? result.analysis : result;

  return (
    <div style={{
      marginTop: "30px",
      padding: "20px",
      border: "1px solid #ddd",
      borderRadius: "8px",
      backgroundColor: "#f9f9f9"
    }}>

      <h2>Threat Analysis Result</h2>

      {/* Show transcript if audio analysis */}
      {result.transcript && (
        <div style={{ marginBottom: "20px" }}>
          <h3>Call Transcript</h3>
          <p>{result.transcript}</p>
        </div>
      )}

      <p><strong>Deepfake Score:</strong> {analysis.deepfake_score}</p>

      <p><strong>Sentiment Score:</strong> {analysis.sentiment_score}</p>

      <p><strong>Threat Level:</strong> {analysis.threat_level}</p>

      <h3 style={{ marginTop: "20px", color: "red" }}>
        Confidence: {analysis.confidence}%
      </h3>

    </div>
  );
}
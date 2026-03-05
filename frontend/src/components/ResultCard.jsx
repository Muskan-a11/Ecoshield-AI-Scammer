export default function ResultCard({ result }) {
    if (!result) return null;

    return (
        <div style={{ marginTop: "20px" }}>
            <h3>Analysis Result</h3>
            <p>Deepfake Score: {result.deepfake_score}</p>
            <p>Sentiment Score: {result.sentiment_score}</p>
            <p>Threat Level: {result.threat_level}</p>
            <h2>Confidence: {result.confidence}%</h2>
        </div>
    );
}
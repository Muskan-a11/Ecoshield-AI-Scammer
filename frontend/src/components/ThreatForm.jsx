import { useState } from "react";
import { analyzeThreat } from "../api";

export default function ThreatForm({ setResult }) {
    const [content, setContent] = useState("");

    const handleAnalyze = async () => {
        const data = await analyzeThreat(content);
        setResult(data);
    };

    return (
        <div>
            <textarea
                placeholder="Paste suspicious content..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
            />
            <button onClick={handleAnalyze}>Analyze</button>
        </div>
    );
}
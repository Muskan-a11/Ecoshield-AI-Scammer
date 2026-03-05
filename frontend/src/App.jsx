import { useState } from "react";
import ThreatForm from "./components/ThreatForm";
import ResultCard from "./components/ResultCard";

function App() {
    const [result, setResult] = useState(null);

    return (
        <div style={{ padding: "40px" }}>
            <h1>Ecoshield Threat Analyzer</h1>
            <ThreatForm setResult={setResult} />
            <ResultCard result={result} />
        </div>
    );
}

export default App;
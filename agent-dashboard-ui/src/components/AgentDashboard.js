// AgentDashboard.js
import { useState } from 'react';

const AGENTS = ["Fitness Coach", "Project Manager", "Legal Advisor", "Data Analyst"];

export default function AgentDashboard() {
  const [prompt, setPrompt] = useState("");
  const [activeAgents, setActiveAgents] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const toggleAgent = (agent) => {
    setActiveAgents(prev =>
      prev.includes(agent) ? prev.filter(a => a !== agent) : [...prev, agent]
    );
  };

  const dispatchAgents = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:5050/dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, agents: activeAgents })
      });
      const data = await res.json();
      if (!data.results) {
        throw new Error("Malformed response");
      }
      const agentResponses = Object.entries(data.results).map(
        ([agent, response]) => `🔹 ${agent}:
${response}`
      );
      setResults(agentResponses);
    } catch (err) {
      console.error("Backend error:", err);
      setResults(["❌ Error connecting to backend. Check if the Flask server is running."]);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-4 border rounded shadow">
      <h2 className="text-xl font-bold mb-4">🧠 Agent Dashboard</h2>

      <div className="mb-4">
        <label className="font-medium">Select Active Agents:</label>
        <div className="flex flex-wrap gap-2 mt-2">
          {AGENTS.map(agent => (
            <button
              key={agent}
              onClick={() => toggleAgent(agent)}
              className={`px-3 py-1 rounded border ${
                activeAgents.includes(agent) ? 'bg-blue-600 text-white' : 'bg-white border-gray-400'
              }`}
            >
              {agent}
            </button>
          ))}
        </div>
      </div>

      <input
        placeholder="Enter prompt (e.g. 'Analyze my fitness trends')"
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        className="w-full mb-4 p-2 border rounded"
      />

      <button
        onClick={dispatchAgents}
        disabled={!prompt.trim() || activeAgents.length === 0 || loading}
        className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? "Dispatching..." : "Dispatch to Agents"}
      </button>

      <div className="mt-6 space-y-3 whitespace-pre-line">
        {results.map((res, i) => (
          <p key={i} className="text-sm bg-gray-100 p-2 rounded shadow-sm">{res}</p>
        ))}
      </div>
    </div>
  );
}

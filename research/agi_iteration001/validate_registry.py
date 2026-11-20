"""Static registry checks; does not instantiate or execute any agents."""
import json
from pathlib import Path

data = json.loads((Path(__file__).parent / "agents_registry.json").read_text())
agents = data["agents"]
assert len(agents) == 55, "Expected 55 agent concepts"
assert [a["id"] for a in agents] == [f"AGI-{i:02}" for i in range(1,56)]
assert len({a["name"] for a in agents}) == 55
assert all(a["status"] == "PROPOSED_UNVERIFIED" for a in agents)
assert all(a["runtime_binding"] is None and a["execution_evidence"] is None for a in agents)
assert all(a["production_enabled"] is False and a["requires_sandbox"] is True for a in agents)
assert all(a["agi_division"] for a in agents)
print("PASS: 55 unique proposed agent roles; zero production-enabled.")

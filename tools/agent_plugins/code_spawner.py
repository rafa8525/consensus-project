from pathlib import Path
from tools.agent_plugins.common import last_git_commit

def run():
    out=[]
    app = Path.home()/ "consensus-project"/"app.py"
    if app.exists():
        src = app.read_text(encoding="utf-8").splitlines()
        need = [("/healthz","test_healthz"),("/metrics","test_metrics"),
                ("/voice_trigger","test_voice_trigger"),("/geo","test_geo")]
        missing=[name for ep,name in need if not any(name in ln for ln in src)]
        if missing:
            out.append({
              "agent":"AI Code Spawner",
              "title":"Add smoke tests for critical endpoints",
              "impact":"medium",
              "action":"Create tools/tests/test_app_smoke.py with pytest for: "+", ".join(missing),
              "evidence":[str(app)], "rationale":"Guard core web paths."
            })
    commit = last_git_commit()
    if commit:
        out.append({
          "agent":"AI Code Spawner",
          "title":"Enable CI pre-push lint (ruff/black) in tools/ci.sh",
          "impact":"low",
          "action":"Add tools/ci.sh + .pre-commit config; run weekly in PA Tasks.",
          "evidence":["git:"+commit], "rationale":"Prevent drift."
        })
    return out

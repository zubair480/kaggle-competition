"""End-to-end smoke test without a GPU: the real swegemma harness drives submission/ against a scripted
fake OpenAI-compatible server. Proves that the submission compiles, that the system prompt templating
({problem_description}) resolves, that tools are bound, and that a patch is extracted and verified.

usage: python scripts/run_smoke_test.py --data DATA_DIR [--task rich_4077] [--submission-dir submission]
The fake model makes one harmless edit to a new source file, so `resolved` is expected to be False;
what matters is that every stage runs and a non-empty patch comes out.
"""
import argparse, asyncio, json, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True); ap.add_argument("--task", default="rich_4077")
ap.add_argument("--submission-dir", default=str(Path(__file__).resolve().parent.parent / "submission"))
ap.add_argument("--out", default="/tmp/smoke_results")
a = ap.parse_args()

SCRIPT = [
    ("run_command", {"command": "git status --short | head -5; ls | head -5"}),
    ("write_file", {"filepath": "smoke_probe_module.py", "content": "VALUE = 1\n"}),
    ("get_status", {}),
    ("submit_patch", {}),
    None,  # final text
]
seen = []

class H(BaseHTTPRequestHandler):
    def log_message(self, *x): pass
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps({"data": [{"id": "fake"}]}).encode())
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        seen.append(body)
        n_assist = sum(1 for m in body["messages"] if m["role"] == "assistant")
        step = SCRIPT[min(n_assist, len(SCRIPT) - 1)]
        if step is None:
            msg = {"role": "assistant", "content": "Done"}; fin = "stop"
        else:
            msg = {"role": "assistant", "content": None, "tool_calls": [{"id": f"call_{n_assist}", "type": "function",
                   "function": {"name": step[0], "arguments": json.dumps(step[1])}}]}; fin = "tool_calls"
        resp = {"id": "x", "object": "chat.completion", "created": int(time.time()), "model": body.get("model", "fake"),
                "choices": [{"index": 0, "message": msg, "finish_reason": fin}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}
        if body.get("stream"):
            self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.end_headers()
            delta = dict(msg);
            if delta.get("tool_calls"): delta["tool_calls"] = [dict(tc, index=0) for tc in delta["tool_calls"]]
            for chunk in ({"choices": [{"index": 0, "delta": delta, "finish_reason": None}]}, {"choices": [{"index": 0, "delta": {}, "finish_reason": fin}]}):
                chunk.update(id="x", object="chat.completion.chunk", created=int(time.time()), model="fake")
                self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")
        else:
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps(resp).encode())

srv = HTTPServer(("127.0.0.1", 0), H); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

import litellm, yaml
from google.adk.models.lite_llm import LiteLlm
from adk_submission import validate_directory
from adk_submission.discovery import discover_declared_models
from adk_submission.registry import ModelRegistry
from swegemma.config import EvalConfig, build_submission_limits
from swegemma.evaluate import Evaluator
from swegemma.models import load_tasks

litellm.drop_params = True
data = Path(a.data); sub = Path(a.submission_dir)
limits, gen = build_submission_limits()
validate_directory(sub, limits=limits)
(model,) = discover_declared_models(sub)
reg = ModelRegistry()
reg.register(model, LiteLlm(model="openai/fake", api_base=f"http://127.0.0.1:{port}/v1", api_key="EMPTY"))
ev = yaml.safe_load((sub / "eval_config.yaml").read_text())["evaluation"]
cfg = EvalConfig(tasks_path=data / "tasks.jsonl", snapshots_dir=data / "snapshots", results_dir=Path(a.out), submission_dir=sub,
                 models=reg, sandbox="subprocess", wheels_dir=data / "wheels", graph_dir=str(data / "graphs"),
                 embeddings_dir=str(data / "embeddings"), timeout_seconds=ev["timeout_seconds"], max_time_minutes=ev["max_time_minutes"],
                 max_tool_calls=ev["max_tool_calls"], max_turns=ev["max_turns"], limits=limits, generation_constraints=gen, display_mode="quiet")
task = next(t for t in load_tasks(data / "tasks.jsonl") if t.instance_id == a.task)
res = asyncio.run(Evaluator(cfg).evaluate_task(task=task))
first = seen[0] if seen else {}
sys_msgs = [m for m in first.get("messages", []) if m["role"] in ("system", "developer")]
sys_text = "\n".join(m["content"] if isinstance(m["content"], str) else json.dumps(m["content"]) for m in sys_msgs)
user_text = next((m["content"] if isinstance(m["content"], str) else json.dumps(m["content"]) for m in first.get("messages", []) if m["role"] == "user"), "")
checks = {
    "model requests made": len(seen) >= 4,
    "system prompt delivered": "expert software engineer" in sys_text,
    "task statement pinned in system prompt": task.problem_statement.strip()[:60] in sys_text,
    "no unresolved template braces": "{problem_description}" not in sys_text and "{hints?}" not in sys_text,
    "tools offered = declared tools": sorted(t["function"]["name"] for t in first.get("tools", [])) == sorted(yaml.safe_load((sub / "agent.yaml").read_text().replace("!include", ""))["tools"]),
    "graph section omitted from task prompt": "Code Intelligence Tools" not in user_text,
    "budget shown to agent matches eval_config": f"Tool calls allowance: {ev['max_tool_calls']} calls" in user_text,
    "non-empty patch extracted": "smoke_probe_module.py" in (res.agent_patch or ""),
    "verification ran": res.test_exit_code is not None and res.test_exit_code != -1,
}
for k, v in checks.items(): print(("PASS" if v else "FAIL"), k)
print("tool_calls:", res.tool_calls, "| resolved:", res.resolved, "| error:", (res.error or "")[:200])
print("sampling sent:", {k: first.get(k) for k in ("temperature", "top_p", "max_tokens", "max_completion_tokens", "extra_body", "chat_template_kwargs", "thinking_token_budget") if k in first})
Path(a.out).mkdir(parents=True, exist_ok=True)
(Path(a.out) / "first_request.json").write_text(json.dumps(first, indent=1))
raise SystemExit(0 if all(checks.values()) else 1)

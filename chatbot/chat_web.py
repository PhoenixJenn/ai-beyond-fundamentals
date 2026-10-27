# chatbot/chat_web.py
import sys, json, queue, pathlib, threading
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))
from llm_client import stream_chat, CONFIG
from flask import Flask, request, Response

app = Flask(__name__)
DONE_MARKER = "\x00DONE\x00"
ERROR_MARKER = "\x00ERROR\x00"




# add above the two routes in chat_web.py
INDEX_HTML = """<!doctype html>
<title>Cost-Meter Chat</title>
<select id="model"></select>
<div id="log" style="white-space:pre-wrap;border:1px solid #ccc;height:320px;overflow-y:auto;padding:10px"></div>
<input id="input"><button id="send">Send</button>
<div id="meter"></div>
<script>
let messages = [], sessionCost = 0;
fetch('/models').then(r => r.json()).then(d => {
  d.models.forEach(m => document.getElementById('model')
    .appendChild(new Option(m, m)));
});

async function send() {
  const input = document.getElementById('input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  messages.push({role: 'user', content: text});
  const log = document.getElementById('log');
  const model = document.getElementById('model').value;
  log.textContent += 'You: ' + text + '\\n' + model + ': ';

  const resp = await fetch('/chat', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({messages, model}),
  });
  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let full = '', buffer = '';
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, {stream: true});
    const doneIdx = buffer.indexOf('\\x00DONE\\x00');
    if (doneIdx !== -1) {
      full += buffer.slice(0, doneIdx);
      log.textContent += buffer.slice(0, doneIdx);
      const meta = JSON.parse(buffer.slice(doneIdx + 6));
      sessionCost += meta.cost;
      document.getElementById('meter').textContent =
        `turn: $${meta.cost.toFixed(6)}, ${meta.elapsed_ms.toFixed(0)}ms | session: $${sessionCost.toFixed(6)}`;
      break;
    }
    full += buffer; log.textContent += buffer; buffer = '';
  }
  messages.push({role: 'assistant', content: full});
  log.textContent += '\\n';
}
document.getElementById('send').onclick = send;
document.getElementById('input').addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
</script>
"""

@app.route("/")
def index():
    return Response(INDEX_HTML, mimetype="text/html")



    

@app.route("/models")
def models():
    return {"models": list(CONFIG.keys())}

@app.route("/chat", methods=["POST"])
def chat():
    body = request.get_json()
    messages, model = body["messages"], body["model"]
    q = queue.Queue()

    def worker():
        try:
            def on_chunk(c):
                q.put(("chunk", c))
            text, cost, elapsed_ms = stream_chat(messages, model, on_chunk=on_chunk)
            q.put(("done", {"cost": cost, "elapsed_ms": elapsed_ms}))
        except Exception as e:
            q.put(("error", str(e)))

    threading.Thread(target=worker, daemon=True).start()

    def generate():
        while True:
            kind, payload = q.get()
            if kind == "chunk":
                yield payload
            elif kind == "done":
                yield DONE_MARKER + json.dumps(payload)
                return
            elif kind == "error":
                yield ERROR_MARKER + payload
                return

    return Response(generate(), mimetype="text/plain")


if __name__ == "__main__":
    app.run(port=5050, debug=True)

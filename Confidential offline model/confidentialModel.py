import os, re, json, requests
import gradio as gr
from openai import OpenAI

# ---------- CONFIG ----------
BASE_URL = os.getenv("OLLAMA_BASE", "http://192.168.1.151:11434/v1")  # Home PC
DEFAULT_MODEL = "phi3:3.8b-mini-4k-instruct-q4_K_M"                    # will auto-check
UI_AUTH = None  # e.g. ("user","strong-password")
LOCAL_UI_ONLY = True  # True → 127.0.0.1 only
# ----------------------------

client = OpenAI(base_url=BASE_URL, api_key="ollama")  # any string ok

def get_models():
    """Query Ollama for tags; return list of names."""
    try:
        # /api/tags is on the non-/v1 base
        base = BASE_URL.replace("/v1", "")
        r = requests.get(f"{base}/api/tags", timeout=5)
        r.raise_for_status()
        data = r.json()
        names = [m["name"] for m in data.get("models", [])]
        return sorted(names)
    except Exception as e:
        return [DEFAULT_MODEL]  # minimal fallback

MODEL_CHOICES = get_models()
if DEFAULT_MODEL not in MODEL_CHOICES and MODEL_CHOICES:
    DEFAULT_MODEL = MODEL_CHOICES[0]

EMAIL_RE   = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_RE   = re.compile(r'(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3}[\s-]?\d{2,4}[\s-]?\d{2,4})')
AMOUNT_RE  = re.compile(r'(?<!\w)(?:USD|EUR|EURO|CHF|\$|€|£)?\s?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?(?!\w)')

def redact(text: str):
    mapping = {}
    def _sub(pattern, tag, t):
        idx = 0
        def repl(m):
            nonlocal idx
            idx += 1
            placeholder = f"<{tag}_{idx}>"
            mapping[placeholder] = m.group(0)
            return placeholder
        return pattern.sub(repl, t)

    out = _sub(EMAIL_RE,  "EMAIL", text)
    out = _sub(PHONE_RE,  "PHONE", out)
    out = _sub(AMOUNT_RE, "AMOUNT", out)
    return out, mapping

def analyze_email(email_text, instruction, model_name, do_redact):
    if not email_text or not email_text.strip():
        return "⚠️ Paste an email or text.", "{}"
    instruction = instruction.strip() or "Summarize, extract action items, risks, and next steps."

    redacted_map = {}
    content = email_text
    if do_redact:
        content, redacted_map = redact(content)

    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system",
                 "content": "You are a concise assistant for internal email analysis. Use bullet points when helpful."},
                {"role": "user",
                 "content": f"Task: {instruction}\n\nEmail:\n{content}"}
            ],
        )
        text = resp.choices[0].message.content.strip()
        return text, json.dumps(redacted_map, indent=2)
    except Exception as e:
        # show the server-side error as-is for quick debugging
        return f"❌ Error: {e}", "{}"

with gr.Blocks(title="Confidential Assistant (Local Ollama)") as demo:
    gr.Markdown("## 🧠 Confidential Assistant (Local Ollama)\nData is processed by your home Ollama server. No internet calls.")

    with gr.Row():
        model_dd = gr.Dropdown(choices=MODEL_CHOICES, value=DEFAULT_MODEL, label="Model", scale=1)
        redact_cb = gr.Checkbox(value=False, label="Redact emails/phones/amounts before sending", scale=1)

    email_tb = gr.Textbox(label="Email or text content", lines=16, placeholder="Paste email here…")
    instr_tb = gr.Textbox(label="Instruction", lines=2,
                          placeholder="E.g., summarize; extract action items; rewrite; detect risks…")

    out_text = gr.Textbox(label="Model Output", lines=16)
    map_text = gr.Textbox(label="Redaction mapping (if enabled)", lines=8)

    run_btn = gr.Button("Run Analysis")
    run_btn.click(analyze_email, [email_tb, instr_tb, model_dd, redact_cb], [out_text, map_text])

# Launch local-only UI on the work PC.
demo.launch(
    share=False,
    server_name="127.0.0.1" if LOCAL_UI_ONLY else "0.0.0.0",
    auth=UI_AUTH
)

# Source-Grounded RAG Chatbot

A web-based chatbot that answers questions **only** from documents you provide, in plain language, with citations back to the source page.

**Current status: Phase 0 complete** — plain chat with a live LLM. Document retrieval is not yet wired in.

---

## Stack

| Component | Technology | Role |
|---|---|---|
| Chat UI + web server | Chainlit | Browser interface, sessions, streaming |
| LLM | DeepSeek or OpenAI (Chat Completions API) | Generates answers |
| Config | python-dotenv | Loads secrets from `.env` |
| Document pipeline | LlamaIndex | *Phase 1+ — not yet added* |
| Vector store | *Undecided* | *Phase 2 — see Open Decisions* |

---

## Requirements

- Python 3.9 or higher
- An API key from [DeepSeek](https://platform.deepseek.com) or [OpenAI](https://platform.openai.com) with credit on the account

---

## Setup

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd rag-chatbot
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

| OS | Activate command |
|---|---|
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |
| Windows (CMD) | `venv\Scripts\activate.bat` |
| macOS / Linux | `source venv/bin/activate` |

Your prompt should now start with `(venv)`. If it does not, nothing below will work.

> PowerShell blocking the script? Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and retry.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

`.env` is **not** in the repository. Create it in the project root.

**For DeepSeek:**

```
LLM_API_KEY=sk-your-key-here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

**For OpenAI:**

```
LLM_API_KEY=sk-your-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

The key and the base URL must belong to the **same provider**. Mixing them returns `401`.

---

## Running

From the project root, with `(venv)` active:

```bash
chainlit run app.py -w
```

Open **http://localhost:8000**

| Flag | Effect |
|---|---|
| `-w` | Watch mode — reloads when you save a Python file |
| `--port 8001` | Use a different port if 8000 is busy |

**Stop the server:** `Ctrl + C`
**Leave the venv:** `deactivate`

> Do not run `python app.py`. Chainlit is a server, not a script.

---

## Daily use

| Task | How |
|---|---|
| Edit code | Save the file; `-w` reloads automatically. Watch the terminal for errors |
| Change LLM provider | Edit `.env`, then **fully restart** the server. `.env` is not auto-reloaded |
| Clear the conversation | Refresh the browser — each page load is a fresh session |
| See errors | Terminal shows the full stack trace; the browser shows a short message |

### Adding a dependency

```bash
pip install <package>
pip freeze | grep <package>     # Windows: pip freeze | findstr <package>
```

Add the package **with its pinned version** to `requirements.txt`. Skipping this means the project will not rebuild on another machine.

---

## Verifying it works

Run all five. Test 4 is the one that matters — it proves you are hitting a real API rather than seeing a silent failure.

| # | Test | Expected |
|---|---|---|
| 1 | Load http://localhost:8000 | Greeting message appears |
| 2 | Ask "What is 2+2?" | Answer streams in **word by word** |
| 3 | Ask "What did I just ask you?" | Correctly recalls the previous question |
| 4 | Set `LLM_API_KEY=sk-wrong` in `.env`, restart, send a message | A visible auth **error** — not a fake answer |
| 5 | Restore the real key, restart | Working again |

---

## Project structure

```
rag-chatbot/
├── venv/               # Installed packages — never committed
├── data/               # Your source documents (empty until Phase 1)
├── .env                # Secrets — never committed
├── .gitignore
├── requirements.txt    # Pinned dependencies
├── chainlit.md         # Splash screen text (empty file hides it)
├── llm.py              # Only file that knows which LLM provider is used
├── app.py              # The server: sessions, messages, streaming
└── README.md
```

### Design notes

- **`llm.py` is isolated on purpose.** Switching between DeepSeek and OpenAI means editing `.env` only — no application code changes.
- **`temperature=0` is deliberate and permanent.** Creativity is how hallucinations enter a grounded system.
- **Conversation history is resent on every request.** The LLM has no memory of its own. History is kept in `cl.user_session` so each browser tab stays separate — a global variable would merge all users' conversations.
- **A failed turn is popped from history.** Otherwise one network error corrupts every subsequent request.

---

## Security

| Rule | Why |
|---|---|
| Never commit `.env` | Keys are scraped from public repos within minutes and billed to you |
| Never paste your key into a chat, screenshot, or issue | Same |
| Set a spending cap in your provider dashboard | Protects against a runaway loop |
| Rotate the key immediately if exposed | Deleting the commit does not undo the leak |

`.gitignore` must exist **before** your first commit. It should contain:

```
venv/
.env
.chainlit/
__pycache__/
data/
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `chainlit: command not found` | venv not active | Reactivate; check for `(venv)` in your prompt |
| `RuntimeError: LLM_API_KEY is missing` | Wrong folder, or file saved as `.env.txt` | `cd` to project root; on Windows enable file extensions and rename |
| `401 Unauthorized` | Key and base URL are from different providers | Match them |
| `429` / `insufficient_quota` | No credit on the account | Add funds |
| Answer appears all at once | Streaming not reaching the browser | Confirm `stream=True` and `stream_token` are both present |
| `Address already in use` | Port 8000 occupied | `chainlit run app.py -w --port 8001` |
| Model not found | Wrong `LLM_MODEL` for the provider | `deepseek-chat` for DeepSeek, `gpt-4o-mini` for OpenAI |

**Check in this order when anything breaks:** venv active → correct folder → `.env` exists and is named correctly → read the terminal stack trace → key and URL match → account has credit.

---

## Roadmap

| Phase | Goal | Status |
|---|---|---|
| 0 | Environment + first LLM call | ✅ Complete |
| 1 | Ingest a PDF, inspect chunks (no AI) | Next |
| 2 | Embeddings + persistent vector store | Blocked — see Open Decisions |
| 3 | Retrieval only, no generation | |
| 4 | Grounded answers with citations | |
| 5 | Refusal + anti-hallucination guards | |
| 6 | Multiple documents + upload UI | |
| 7 | Robust PDF handling (OCR, tables) | |
| 8 | Evaluation set | |
| 9 | Hardening + deployment | |

### Build rules

1. One phase at a time; pass the verification gate before advancing.
2. Debug retrieval before generation — always in that order.
3. Read your raw chunks. Most RAG bugs are visible in the extracted text.
4. Check citations manually. Plausible is not the same as correct.
5. Keep LLM and embedding providers behind a single file.

---

## Open decisions

These block Phase 2 and need answers before the vector store is built.

| # | Question | Blocks |
|---|---|---|
| 1 | Vector store: in-memory, ChromaDB, or Postgres + pgvector? | Phase 2 |
| 2 | Embeddings: external API or a local model? | Phase 2 |
| 3 | May documents be sent to external APIs, or must they stay on our server? | Phases 2, 4 |
| 4 | Public access without login? | Phase 9 |
| 5 | Corpus size — how many documents and pages? | Phase 2 sizing |

Note: an in-memory vector store does not survive a restart. Anything intended for real use needs ChromaDB or Postgres.

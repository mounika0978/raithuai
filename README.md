# RaithuMitra AI — runnable demo prototype

A small FastAPI + HTML/CSS/JavaScript prototype for rain-fed farmers in Andhra Pradesh. Focus: groundnut and red gram / pulses, with cautious rule-based responses and links to official resources.

## Architecture

```text
Browser (HTML/CSS/JS)
  ├─ farmer profile + chat + voice/photo controls
  └─ POST /api/chat
          ↓
      FastAPI (main.py)
          ↓
      transparent keyword rules + data/knowledge_base.json
          ↓
      answer + source metadata + expert-confirmation flag
```

No Python code is needed in the browser, but **Python is needed to run this FastAPI version locally or deploy its backend**. If you need a strictly no-Python version, use the separate static GitHub Pages project.

## Folder structure

```text
raithumitra_live_demo/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── data/
│   └── knowledge_base.json
└── static/
    ├── index.html
    ├── styles.css
    └── app.js
```

## Run locally (Windows)

1. Install Python 3.11 or newer from https://www.python.org/downloads/ and enable **Add Python to PATH**.
2. Extract this ZIP.
3. Open Command Prompt or PowerShell inside the extracted folder.
4. Run:

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can skip activation and run:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

If activation worked, run:
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

5. Open http://127.0.0.1:8000
6. API health check: http://127.0.0.1:8000/api/health
7. API docs: http://127.0.0.1:8000/docs

## Demo questions

- “I grow groundnut in Anantapur and rainfall has been irregular. What should I check?”
- “What should I check before sowing groundnut?”
- “What should I monitor during flowering?”
- “My crop leaves look yellow. Can you diagnose this?”
- “Where can I verify current government schemes for farmers?”
- Telugu: “వర్షం ఆలస్యం అయితే ఏమి పరిశీలించాలి?”

## Data source and trust labels

`data/knowledge_base.json` links to official portals:
- IMD Mausam: https://mausam.imd.gov.in/
- ANGRAU: https://angrau.ac.in/
- ICAR: https://icar.org.in/
- AP Agriculture portal: https://apagrisnet.gov.in/

The current knowledge-base content is a **small starter set**, not a validated crop recommendation corpus. Records marked `illustrative` are demo rules. The app links to official websites but does not claim every general statement was verified against a particular document or update date. Verify current crop recommendations with ANGRAU, a local KVK or the agriculture department before field action.

## Features

- Chat interface with quick prompts, new conversation, profile form, English/Telugu UI switch.
- Rule-based responses personalised by crop, location and growth stage.
- Sources shown as links with source type and update metadata.
- Voice input when the browser supports Web Speech API.
- Text-to-speech where supported.
- Photo upload with 5 MB limit and clear no-diagnosis disclaimer.
- `/api/health` and `/docs`.

## Limitations

- **No live weather API is configured.** Weather-related answers explicitly say current forecast data are unavailable and link to IMD.
- **No LLM is connected by default.** Chat responses are transparent keyword/rule-based demo answers. `OPENAI_API_KEY` is only a placeholder for future backend integration; this starter does not send it anywhere.
- **No genuine crop-image model.** Photo upload validates and receives an image but never claims to diagnose it.
- No official scheme account access, application lookup, insurance records or approval guarantee.
- Profile is held in page memory for the current session; no database or persistent server-side farmer records are used.
- The sample source list is not an endorsement of specific agronomic actions. No exact chemical doses are given.

## Environment variables

See `.env.example`. No environment variable is required for demo mode. If you later integrate an AI or weather provider, implement it only in the backend, use environment variables in hosting settings, and never commit real secrets.

## Troubleshooting

- `python is not recognized`: reinstall Python and select “Add Python to PATH”, or use `py -m venv .venv`.
- `ModuleNotFoundError`: install packages with `pip install -r requirements.txt`.
- `uvicorn is not recognized`: run `python -m uvicorn main:app --reload`.
- Browser shows a blank page: confirm server is running and visit `http://127.0.0.1:8000`, not by double-clicking `index.html`.
- `404 /static/...`: ensure `static/` folder is alongside `main.py`.
- Photo upload error: use JPG/PNG/WebP and keep it at 5 MB or less.
- Voice input unavailable: use a supported browser and allow microphone permission; otherwise type in English or Telugu.
- Port already in use: run `python -m uvicorn main:app --reload --port 8001`.

## Test checklist

- [ ] Home page opens and `/api/health` returns `status: ok`.
- [ ] Send rainfall question; answer clearly states live weather is not configured.
- [ ] Change crop/stage profile and ask crop-stage question.
- [ ] Switch language to Telugu and test a rainfall question.
- [ ] Quick-action buttons send their sample question.
- [ ] New conversation clears the displayed chat.
- [ ] Speaker reads the last answer if browser speech synthesis exists.
- [ ] Microphone works if browser recognition is supported, or shows a fallback.
- [ ] Upload JPG/PNG/WebP <= 5 MB; app states no crop diagnosis model is configured.
- [ ] Source links open official organisation portals.

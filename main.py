from __future__ import annotations
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "knowledge_base.json"
with DATA_PATH.open("r", encoding="utf-8") as f:
    KB = json.load(f)

app = FastAPI(title="RaithuMitra AI Demo", version="1.0.0",
              description="Rule-based farming assistant prototype. No live weather unless configured.")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

class FarmerProfile(BaseModel):
    village: str = ""
    mandal: str = ""
    district: str = "Anantapur"
    crop: str = "groundnut"
    sowing_date: str = ""
    growth_stage: str = "unknown"
    soil_type: str = "unknown"
    water_availability: str = "rainfed"
    language: str = "en"

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    profile: FarmerProfile = Field(default_factory=FarmerProfile)

class ChatResponse(BaseModel):
    answer: str
    mode: str
    sources: list[dict[str, str]]
    needs_expert: bool = False
    weather_status: str = "not_configured"

def matching_sources(tags: list[str]) -> list[dict[str, str]]:
    found = []
    for item in KB["items"]:
        if any(tag in item.get("tags", []) for tag in tags):
            found.append({
                "title": item["title"],
                "organisation": item["organisation"],
                "url": item.get("url", ""),
                "updated": item.get("updated", "Date not provided"),
                "type": item.get("type", "illustrative")
            })
    # avoid duplicates
    unique = []
    seen = set()
    for item in found:
        key = (item["title"], item["organisation"])
        if key not in seen:
            unique.append(item); seen.add(key)
    return unique[:3]

def answer_rule_based(message: str, p: FarmerProfile) -> tuple[str, list[dict[str, str]], bool]:
    q = message.lower()
    lang_te = p.language == "te"
    crop = p.crop.replace("_", " ")
    location = ", ".join(x for x in [p.village.strip(), p.mandal.strip(), p.district.strip()] if x)
    location = location or p.district or "your area"
    stage = p.growth_stage.replace("_", " ")
    stage_label = stage if stage != "unknown" else "not specified"
    sources: list[dict[str, str]] = []
    expert = False

    if any(k in q for k in ["scheme", "government", "insurance", "pm kisan", "పథకం", "ప్రభుత్వ"]):
        sources = matching_sources(["schemes"])
        if lang_te:
            answer = ("ప్రభుత్వ పథకాలకు అర్హత, దరఖాస్తు స్థితి మరియు అవసరమైన పత్రాలు పథకం/రాష్ట్ర నియమాలపై ఆధారపడతాయి. "
                      "ఈ డెమో మీ వ్యక్తిగత దరఖాస్తు రికార్డులను చూడదు, ఆమోదాన్ని హామీ ఇవ్వదు. అధికారిక పోర్టల్ లేదా స్థానిక వ్యవసాయ/రెవెన్యూ కార్యాలయంలో తాజా వివరాలు నిర్ధారించండి.")
        else:
            answer = ("Scheme eligibility and documents depend on the specific scheme and current rules. This demo cannot access private application records or guarantee approval. "
                      "Use the official scheme portal or confirm current requirements with your local agriculture/revenue office.")
        return answer, sources, True

    if any(k in q for k in ["photo", "image", "leaf", "disease", "pest", "yellow", "spots", "ఆకు", "తెగులు"]):
        sources = matching_sources(["crop_problem"])
        if lang_te:
            answer = ("ఫోటోను స్వీకరించగలను, కానీ ఈ డెమోలో నిజమైన మొక్కల-వ్యాధి గుర్తింపు మోడల్ లేదు. పసుపు రంగు/మచ్చలకు అనేక కారణాలు ఉండవచ్చు. "
                      "మొత్తం మొక్క, ప్రభావిత ఆకుల దగ్గరి ఫోటోలు తీసి, సమస్య ఎప్పుడు మొదలైందో మరియు ఇటీవల వర్షం/పిచికారీ వివరాలను నమోదు చేయండి. మందు వాడే ముందు KVK లేదా వ్యవసాయ అధికారిని సంప్రదించండి.")
        else:
            answer = ("I can accept a photo, but this demo has no genuine crop-disease identification model. Yellowing or spots can have several causes. "
                      "Record when symptoms began, recent rain/spraying, and take clear whole-plant plus close-up photos. Ask your KVK/agriculture officer before applying a pesticide.")
        return answer, sources, True

    if any(k in q for k in ["rain", "rainfall", "weather", "dry spell", "drought", "forecast", "వర్షం", "వాన", "కరువు"]):
        sources = matching_sources(["rainfall", crop, "groundnut"])
        if lang_te:
            answer = (f"మీ పంట: {crop}; ప్రాంతం: {location}; పంట దశ: {stage_label}.\\n\\n"
                      "ఈ డెమోలో ప్రత్యక్ష వాతావరణ API కనెక్ట్ కాలేదు కాబట్టి తాజా వర్షపాతం/వర్ష సూచనను చూపించడం లేదు. నమూనా డేటాను నిజమైనదిగా భావించవద్దు.\\n"
                      "• IMD తాజా సూచనను మరియు స్థానిక KVK/వ్యవసాయ శాఖ సలహాను పరిశీలించండి.\\n"
                      "• పొలంలో వాస్తవ నేల తేమ, నీరు నిలిచే పరిస్థితి, పంట దశను చూసి నిర్ణయం తీసుకోండి.\\n"
                      "• వర్షం ఆలస్యం అయిందని మాత్రమే పంట మార్చడం లేదా ఖరీదైన ఇన్‌పుట్స్ కొనడం నిర్ణయించవద్దు.\\n"
                      "• సందేహం ఉంటే స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.")
        else:
            answer = (f"Your crop: {crop}; area: {location}; growth stage: {stage_label}.\\n\\n"
                      "Live weather is not connected in this demo, so I cannot report current rainfall or forecast values. Do not treat sample data as real.\\n"
                      "• Check the latest IMD forecast and local KVK/agriculture department advisory.\\n"
                      "• Base field decisions on actual soil moisture, drainage and crop stage.\\n"
                      "• Do not change crops or buy costly inputs based only on a short-term forecast.\\n"
                      "• Ask a local agriculture officer if conditions are uncertain.")
        return answer, sources, True

    if any(k in q for k in ["sow", "sowing", "seed", "planting", "విత్త", "విత్తనం"]):
        sources = matching_sources(["sowing", crop, "groundnut"])
        if lang_te:
            answer = (f"{crop} విత్తే ముందు ({location}):\\n"
                      "• తాజా స్థానిక వర్ష సూచన మరియు పొలంలోని నేల తేమను పరిశీలించండి.\\n"
                      "• మీ ప్రాంతానికి ANGRAU/KVK సూచించిన రకం, విత్తే సమయం, విత్తన నాణ్యతను నిర్ధారించండి.\\n"
                      "• నేల రకం, నీరు బయటకు వెళ్లే పరిస్థితి, విత్తే పరికరాల లభ్యతను పరిగణించండి.\\n"
                      "ఈ డెమో ఖచ్చితమైన విత్తే తేదీ లేదా విత్తన మోతాదును సూచించదు; స్థానిక సిఫార్సును నిర్ధారించండి.")
        else:
            answer = (f"Before sowing {crop} in {location}:\\n"
                      "• Check the latest local forecast and actual soil moisture.\\n"
                      "• Confirm locally recommended variety, sowing window and seed quality with ANGRAU/KVK or the agriculture department.\\n"
                      "• Consider soil type, drainage and whether the field can be worked safely.\\n"
                      "This demo does not prescribe an exact sowing date or seed rate; verify local recommendations.")
        return answer, sources, True

    if any(k in q for k in ["stage", "flower", "pod", "growth", "crop guidance", "పూత", "పంట దశ"]):
        sources = matching_sources(["crop_stage", crop, "groundnut"])
        if lang_te:
            answer = (f"{crop} — పంట దశ: {stage_label}.\\n"
                      "పంట నిలువు, కలుపు, ఆకుల రంగు, పురుగు/వ్యాధి లక్షణాలు మరియు నేల తేమను క్రమంగా పరిశీలించండి. పూత లేదా కాయ ఏర్పడే సమయంలో నీటి ఒత్తిడి పంటపై ప్రభావం చూపవచ్చు; కానీ చర్య నేల, పంట స్థితి, నీటి లభ్యతపై ఆధారపడుతుంది. "
                      "ఖచ్చితమైన ఎరువు/పురుగుమందు మోతాదు కోసం ఈ డెమోను ఆధారంగా తీసుకోకండి; స్థానిక KVK సలహా పొందండి.")
        else:
            answer = (f"{crop.title()} — growth stage: {stage_label}.\\n"
                      "Regularly check crop stand, weeds, leaf colour, pest/disease symptoms and soil moisture. Moisture stress can matter at sensitive stages, but actions depend on the crop, soil and actual field conditions. "
                      "Do not use this demo to choose exact fertiliser or pesticide doses; get crop-specific advice from your local KVK/agriculture officer.")
        return answer, sources, True

    sources = matching_sources(["general", crop])
    if lang_te:
        answer = ("నేను వర్షపాతం ప్రణాళిక, విత్తే ముందు పరిశీలనలు, పంట దశ, నేల తేమ మరియు పథకాల గురించి సహాయం చేయగలను. "
                  "మీ ప్రశ్నను కొంచెం వివరంగా అడగండి. ఈ డెమోలో ప్రత్యక్ష వాతావరణం లేదా నిజమైన AI మోడల్ లేదు; ముఖ్యమైన నిర్ణయాలకు స్థానిక నిపుణుడి సలహా తీసుకోండి.")
    else:
        answer = ("I can help with rainfall planning, pre-sowing checks, crop-stage observations, soil-moisture conservation and scheme information. "
                  "Could you share a little more detail? This demo has no live weather feed or connected LLM; verify important decisions with your local agriculture expert.")
    return answer, sources, False

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "rule-based-demo", "live_weather": False, "llm_connected": bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    answer, sources, expert = answer_rule_based(body.message, body.profile)
    return ChatResponse(answer=answer, mode="demo", sources=sources, needs_expert=expert, weather_status="not_configured")

@app.post("/api/crop-photo")
async def crop_photo(file: UploadFile = File(...)):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Please upload a JPG, PNG or WebP image.")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be 5 MB or smaller.")
    return {"message": "Photo received for the demo, but no crop-image diagnosis model is configured. Please consult your local KVK/agriculture officer before treating the crop.", "filename": file.filename, "diagnosis": None}

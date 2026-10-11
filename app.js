const $ = s => document.querySelector(s);
const messagesEl = $("#messages");
let history = [];
let lastAnswer = "";
const lang = () => $("#language").value;

function profile() {
  return {
    village: $("#village").value.trim(),
    mandal: $("#mandal").value.trim(),
    district: $("#district").value,
    crop: $("#crop").value,
    sowing_date: $("#sowing-date").value,
    growth_stage: $("#growth-stage").value,
    soil_type: $("#soil").value,
    water_availability: $("#water").value,
    language: lang()
  };
}
function clearWelcome() {
  const welcome = messagesEl.querySelector(".welcome-wrap");
  if (welcome) welcome.remove();
}
function appendMessage(text, role, sources=[], expert=false) {
  clearWelcome();
  const row = document.createElement("div");
  row.className = `message ${role}`;
  const avatar = document.createElement("div"); avatar.className = "avatar"; avatar.textContent = role === "user" ? "👩‍🌾" : "🌱";
  const body = document.createElement("div"); body.className = "message-body";
  const textNode = document.createElement("div"); textNode.textContent = text; body.appendChild(textNode);
  if (sources.length) {
    const wrap = document.createElement("div"); wrap.className = "sources";
    const heading = document.createElement("b"); heading.textContent = lang() === "te" ? "సూచనలు / మూలాలు" : "Sources & references"; wrap.appendChild(heading);
    sources.forEach(s => {
      const line = document.createElement("div");
      const link = document.createElement("a"); link.href = s.url || "#"; link.target = "_blank"; link.rel = "noopener noreferrer";
      link.textContent = `${s.organisation}: ${s.title} (${s.updated})`;
      if (!s.url) { link.removeAttribute("href"); link.style.textDecoration = "none"; }
      line.appendChild(link);
      const kind = document.createElement("small"); kind.textContent = s.type === "illustrative" ? (lang() === "te" ? "నమూనా నియమం" : "Illustrative demo rule") : (lang() === "te" ? "బాహ్య మూలం — తాజా వివరాలు చూడండి" : "External source — check for latest details");
      line.appendChild(document.createElement("br")); line.appendChild(kind); wrap.appendChild(line);
    });
    body.appendChild(wrap);
  }
  if (expert) {
    const flag = document.createElement("div"); flag.className = "expert-flag";
    flag.textContent = lang() === "te" ? "స్థానిక KVK / వ్యవసాయ అధికారితో నిర్ధారించండి." : "Please verify with your local KVK / agriculture officer.";
    body.appendChild(flag);
  }
  const meta = document.createElement("div"); meta.className = "message-meta"; meta.textContent = role === "user" ? "You · now" : "RaithuMitra · demo response"; body.appendChild(meta);
  row.append(avatar, body); messagesEl.appendChild(row); messagesEl.scrollTop = messagesEl.scrollHeight;
  if (role === "assistant") lastAnswer = text;
}
function typing(on) { $("#typing").classList.toggle("hidden", !on); }
async function ask(question) {
  question = question.trim();
  if (!question) return;
  $("#question").value = "";
  $("#send").disabled = true;
  appendMessage(question, "user");
  history.push({role:"user", content:question});
  typing(true);
  try {
    const res = await fetch("/api/chat", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:question, profile:profile()})
    });
    if (!res.ok) throw new Error(`Server returned ${res.status}`);
    const data = await res.json();
    typing(false);
    appendMessage(data.answer, "assistant", data.sources || [], data.needs_expert);
    history.push({role:"assistant", content:data.answer});
  } catch (err) {
    typing(false);
    appendMessage(lang() === "te"
      ? "సమాధానం పొందలేకపోయాను. ఇంటర్నెట్/సర్వర్‌ను తనిఖీ చేసి మళ్లీ ప్రయత్నించండి."
      : "I couldn't get a response. Check that the app server is running and try again. If the problem continues, reload the page.", "assistant");
  } finally { $("#send").disabled = false; $("#question").focus(); }
}
$("#chat-form").addEventListener("submit", e => { e.preventDefault(); ask($("#question").value); });
document.querySelectorAll("[data-question]").forEach(b => b.addEventListener("click", () => ask(b.dataset.question)));
$("#profile-form").addEventListener("submit", e => {
  e.preventDefault();
  const p = profile();
  appendMessage((lang() === "te" ? "మీ పొలం వివరాలు ఈ సెషన్ కోసం నవీకరించబడ్డాయి: " : "Farm profile updated for this session: ") +
    [p.village, p.mandal, p.district, p.crop, p.growth_stage, p.soil_type, p.water_availability].filter(Boolean).join(" · "), "assistant");
});
$("#new-chat").addEventListener("click", () => {
  history = []; lastAnswer = "";
  messagesEl.innerHTML = `<div class="welcome-wrap"><div class="welcome-mark">🌾</div><div class="welcome-kicker">${lang()==="te"?"నమస్కారం · స్వాగతం":"NAMASKARAM · WELCOME"}</div><h2>${lang()==="te"?"ఈ రోజు మీ పొలానికి ఎలా సహాయం చేయగలను?":"How can I help your farm today?"}</h2><p>${lang()==="te"?"మీ పొలంలో ఏమి జరుగుతోందో చెప్పండి. వర్షం, విత్తడం మరియు పంట దశ గురించి అడగండి.":"Tell me what is happening in your field. Ask about rainfall, sowing and crop stage."}</p><div class="welcome-bilingual">మీ పంట గురించి అడగండి — Ask about your crop.</div></div>`;
});
$("#speak-last").addEventListener("click", () => {
  if (!lastAnswer) { alert(lang()==="te"?"ముందుగా సమాధానం పొందండి.":"Ask a question first to hear an answer."); return; }
  if (!("speechSynthesis" in window)) { alert(lang()==="te"?"ఈ బ్రౌజర్‌లో వాయిస్ సదుపాయం లేదు.":"Text-to-speech is not supported in this browser."); return; }
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(lastAnswer);
  utterance.lang = lang() === "te" ? "te-IN" : "en-IN";
  speechSynthesis.speak(utterance);
});
$("#mic").addEventListener("click", () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { alert(lang()==="te"?"మీ బ్రౌజర్‌లో వాయిస్ టైపింగ్ లేదు. తెలుగులో టైప్ చేయవచ్చు.":"Voice input is not supported in this browser. You can type in English or Telugu."); return; }
  const rec = new SR(); rec.lang = lang() === "te" ? "te-IN" : "en-IN"; rec.interimResults = false;
  $("#mic").textContent = "⏺️";
  rec.onresult = e => { $("#question").value = e.results[0][0].transcript; };
  rec.onerror = () => alert("Voice input could not be captured. Please try typing.");
  rec.onend = () => $("#mic").textContent = "🎙️";
  rec.start();
});
$("#photo").addEventListener("change", async e => {
  const file = e.target.files[0]; if (!file) return;
  if (file.size > 5*1024*1024) { alert("Image must be 5 MB or smaller."); e.target.value = ""; return; }
  appendMessage(`Photo selected: ${file.name}`, "user");
  const form = new FormData(); form.append("file", file);
  typing(true);
  try {
    const res = await fetch("/api/crop-photo", {method:"POST", body:form});
    const data = await res.json();
    typing(false);
    if (!res.ok) throw new Error(data.detail || "Upload failed");
    appendMessage(data.message, "assistant", [], true);
  } catch(err) { typing(false); appendMessage(err.message || "Photo upload failed.", "assistant"); }
  e.target.value = "";
});
$("#language").addEventListener("change", () => {
  const l = lang();
  document.querySelectorAll("[data-en]").forEach(el => el.textContent = el.dataset[l]);
  $("#question").placeholder = l === "te" ? "మీ పొలం గురించి అడగండి…" : "Ask RaithuMitra about your field…";
  $("#connection").textContent = l === "te" ? "● డెమో నియమాలు పనిచేస్తున్నాయి" : "● Demo rules active";
});

import streamlit as st
from anthropic import Anthropic
import base64
import os
import json
from datetime import datetime

KEY_FILE = os.path.join(os.path.dirname(__file__), ".apikey")
LOG_FILE = os.path.join(os.path.dirname(__file__), "log.json")

def load_key():
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_key(key):
    with open(KEY_FILE, "w") as f:
        f.write(key.strip())

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_log_entry(entry):
    log = load_log()
    log.insert(0, entry)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

# ── Translations ──────────────────────────────────────────────────────────────
UI = {
    "en": {
        "subtitle":         "His messages, decoded. Olivia, protected. Laura, restored.",
        "tab_messages":     "💬 His Messages",
        "tab_olivia":       "💛 Olivia Mode",
        "tab_log":          "📋 Log",
        "context_expander": "Add context about this specific message (optional)",
        "context_label":    "Anything that helps - time of day, what triggered it, what happened before:",
        "context_ph":       "E.g. 'He sent this at 11pm after I told him I was running a race this weekend'",
        "msg_header":       "### His message",
        "tab_paste":        "Paste text",
        "tab_screenshot":   "Upload screenshot",
        "paste_label":      "Paste his text or email:",
        "paste_ph":         "Paste exactly what he said...",
        "upload_label":     "Upload a screenshot:",
        "analyze_btn":      "Analyze & Get Responses",
        "spinner_analyze":  "Reading between his lines...",
        "error_no_input":   "Paste his message or upload a screenshot first.",
        "tactic_label":     "🎯 WHAT HE JUST DID",
        "save_label":       "📸 DOCUMENT THIS - worth saving a screenshot",
        "r1_label":         "🔥 WHAT YOU REALLY WANT TO SAY - do not send",
        "r2_label":         "💙 WHAT TO ACTUALLY SEND",
        "copy_label":       "Copy to send:",
        "mood_title":       "Before you send that - remember who you actually are:",
        "mood_body":        """🏅 &nbsp;Ironman finisher. Multiple races.<br>
🏔️ &nbsp;Leadville 100 invitee - <em>invitation only</em>. Elite athletes only.<br>
⚖️ &nbsp;Successful attorney. Steady career. Never been fired.<br>
👯 &nbsp;Surrounded by real friends. Well-traveled. Fully alive.<br>
💛 &nbsp;A mother who actually shows up.""",
        "mood_closing":     "Send Response 2 from that person. Not from who he says you are.",
        "error_generic":    "Something went wrong:",
        "olivia_header":    "### What to say to Olivia",
        "olivia_sub":       "Use this when she calls crying during his week, or when she comes home upset.",
        "always_label":     "💜 PHRASES LAURA CAN ALWAYS SAY - no matter what happened",
        "always_phrases":   (
            '&nbsp;• &nbsp;"I love you so much, and that will never ever change."<br>'
            '&nbsp;• &nbsp;"Your feelings make complete sense. It\'s okay to feel sad / mad / disappointed."<br>'
            '&nbsp;• &nbsp;"You didn\'t do anything wrong. This is not your fault."<br>'
            '&nbsp;• &nbsp;"Grown-up stuff is never your job to fix."<br>'
            '&nbsp;• &nbsp;"I\'m always here when you need me."<br>'
            '&nbsp;• &nbsp;"You are such a strong kid and I am so proud of you."'
        ),
        "scripts_header":   "### Get scripts for right now",
        "scenario_label":   "What's happening?",
        "scenarios": [
            "He won't take her to gymnastics or an activity",
            "He won't take her to a birthday party or social event",
            "He yelled at her or she's scared of him",
            "She's crying and begging mom to come fix it",
            "She says dad said something mean or unfair",
            "She's asking why daddy doesn't do things with her",
            "She's had a hard week with him and just got home",
            "He's being cold or ignoring her",
            "She's asking why mom and dad aren't together",
        ],
        "details_label":    "Any specific details? (optional - makes the scripts sharper):",
        "details_ph":       "E.g. 'She called crying because he said he had too much work and couldn't take her to gymnastics.'",
        "olivia_btn":       "Get Scripts for Olivia",
        "spinner_olivia":   "Getting the right words...",
        "scripts_label":    "💬 WHAT LAURA CAN SAY TO OLIVIA RIGHT NOW",
        "log_header":       "Communication Log",
        "log_empty":        "No messages analyzed yet. Your log will appear here after you use the His Messages tab.",
        "export_btn":       "⬇️ Export Full Log (for your attorney)",
        "log_his_msg":      "His message:",
        "log_tactic":       "Tactic:",
        "log_save":         "Saved for records:",
        "log_sent":         "What she sent:",
        "disclaimer":       "This app is for emotional support only. It is not legal advice and is not a substitute for a licensed attorney.",
        "lang_label":       "Language / Idioma",
    },
    "es": {
        "subtitle":         "Sus mensajes, descifrados. Olivia, protegida. Laura, restaurada.",
        "tab_messages":     "💬 Sus Mensajes",
        "tab_olivia":       "💛 Modo Olivia",
        "tab_log":          "📋 Registro",
        "context_expander": "Agrega contexto sobre este mensaje (opcional)",
        "context_label":    "Cualquier cosa que ayude - hora del dia, que lo provoco, que paso antes:",
        "context_ph":       "Ej. 'Lo envio a las 11pm despues de que le dije que iba a correr este fin de semana'",
        "msg_header":       "### Su mensaje",
        "tab_paste":        "Pegar texto",
        "tab_screenshot":   "Subir captura",
        "paste_label":      "Pega su texto o correo aqui:",
        "paste_ph":         "Pega exactamente lo que dijo...",
        "upload_label":     "Sube una captura de pantalla:",
        "analyze_btn":      "Analizar y Obtener Respuestas",
        "spinner_analyze":  "Leyendo entre sus lineas...",
        "error_no_input":   "Pega su mensaje o sube una captura primero.",
        "tactic_label":     "🎯 LO QUE ACABA DE HACER",
        "save_label":       "📸 GUARDA ESTO - vale la pena tomar una captura",
        "r1_label":         "🔥 LO QUE REALMENTE QUIERES DECIR - no lo envies",
        "r2_label":         "💙 LO QUE DEBES ENVIAR",
        "copy_label":       "Copia para enviar:",
        "mood_title":       "Antes de enviar - recuerda quien eres realmente:",
        "mood_body":        """🏅 &nbsp;Finalista de Ironman. Multiples carreras.<br>
🏔️ &nbsp;Invitada al Leadville 100 - <em>solo por invitacion</em>. Solo atletas de elite.<br>
⚖️ &nbsp;Abogada exitosa. Carrera estable. Nunca ha sido despedida.<br>
👯 &nbsp;Rodeada de amigos de verdad. Viajera. Completamente viva.<br>
💛 &nbsp;Una madre que realmente se presenta.""",
        "mood_closing":     "Envia la Respuesta 2 desde esa persona. No desde quien el dice que eres.",
        "error_generic":    "Algo salio mal:",
        "olivia_header":    "### Que decirle a Olivia",
        "olivia_sub":       "Usalo cuando llame llorando durante la semana de el, o llegue a casa alterada.",
        "always_label":     "💜 FRASES QUE LAURA SIEMPRE PUEDE DECIR - sin importar lo que paso",
        "always_phrases":   (
            '&nbsp;• &nbsp;"Te quiero muchisimo, y eso nunca va a cambiar."<br>'
            '&nbsp;• &nbsp;"Tus sentimientos tienen todo el sentido. Esta bien sentirse triste / enojada / decepcionada."<br>'
            '&nbsp;• &nbsp;"No hiciste nada malo. Esto no es tu culpa."<br>'
            '&nbsp;• &nbsp;"Los asuntos de adultos nunca son tu trabajo de resolver."<br>'
            '&nbsp;• &nbsp;"Siempre estoy aqui cuando me necesitas."<br>'
            '&nbsp;• &nbsp;"Eres una nina muy fuerte y estoy muy orgullosa de ti."'
        ),
        "scripts_header":   "### Guiones para ahora mismo",
        "scenario_label":   "Que esta pasando?",
        "scenarios": [
            "El no la quiere llevar a gimnasia o alguna actividad",
            "El no la quiere llevar a una fiesta de cumpleanos o evento social",
            "El le grito o ella tiene miedo de el",
            "Ella llora y le suplica a mama que venga a arreglar todo",
            "Ella dice que papa dijo algo cruel o injusto",
            "Ella pregunta por que papa no hace cosas con ella",
            "Tuvo una semana dificil con el y acaba de llegar a casa",
            "El esta siendo frio o la esta ignorando",
            "Ella pregunta por que mama y papa no estan juntos",
        ],
        "details_label":    "Detalles especificos? (opcional - hace los guiones mas precisos):",
        "details_ph":       "Ej. 'Llamo llorando porque el dijo que tenia demasiado trabajo para llevarla a gimnasia.'",
        "olivia_btn":       "Obtener Guiones para Olivia",
        "spinner_olivia":   "Buscando las palabras correctas...",
        "scripts_label":    "💬 LO QUE LAURA PUEDE DECIRLE A OLIVIA AHORA MISMO",
        "log_header":       "Registro de Comunicaciones",
        "log_empty":        "Aun no hay mensajes analizados. Tu registro aparecera aqui despues de usar la pestana Sus Mensajes.",
        "export_btn":       "⬇️ Exportar Registro Completo (para tu abogada)",
        "log_his_msg":      "Su mensaje:",
        "log_tactic":       "Tactica:",
        "log_save":         "Guardado:",
        "log_sent":         "Lo que envio:",
        "disclaimer":       "Esta aplicacion es solo para apoyo emocional. No es asesoramiento legal y no sustituye a un abogado con licencia.",
        "lang_label":       "Language / Idioma",
    }
}

def t(key):
    lang = st.session_state.get("lang", "en")
    return UI[lang].get(key, UI["en"].get(key, key))

# ── AI context ────────────────────────────────────────────────────────────────
ERICK_CONTEXT = """
You are analyzing messages from Erick, the ex-husband of Laura.

Known patterns about Erick:
- Tells Laura she is a "bad mom" because she trains for elite athletic competitions (Ironman races, Leadville 100 invitee - invitation only). His logic: watching football on the couch is "good parenting" because he's present, but her training is bad parenting because she has to leave.
- During his own custody weeks, he sits on the couch while their daughter Olivia plays alone or on a tablet all day. Zero engagement.
- He blames Laura whenever Olivia gets a normal childhood illness ("she always gets sick on your watch"), despite his complete non-engagement when he has her.
- He wouldn't let Laura display her hundreds of race medals - a normal athlete tradition - controlling her achievements even in their shared home.
- He has been fired from multiple jobs (at least 3). He tells people at work that everything gets dumped on him and he saves the day. He almost certainly underperforms.
- He is significantly less educated, motivated, and intellectually capable than Laura, who is a successful attorney with a stable career throughout their marriage and after.
- He has very few friends. Refuses therapy. Is homophobic and judgmental.
- During his own custody weeks, he regularly dumps Olivia back on Laura claiming he's "too busy with work" - then doesn't engage when he does have her.
- He has eroded Laura's confidence so thoroughly that she now questions her own good decisions.
- Core dynamic: deeply insecure, threatened by Laura's competence, social life, achievements, and independence. Tears her down to feel better about himself. Uses Olivia as a weapon to wound Laura.
- Psychological profile: NOT classic narcissism. Closer to covert passive-aggressive personality with fragile ego, victim mentality, and compensatory control behaviors. Projects his failures onto Laura.

Laura's actual profile:
- Successful attorney, steady employment throughout their marriage and after
- Elite endurance athlete - Ironman finisher, Leadville 100 invitee (invitation only, elite athletes only)
- Hundreds of race medals
- Highly social, widely liked, active, engaged, loving mother
- Has been systematically undermined by Erick until she questions her own judgment
- Daughter: Olivia (elementary school age)
"""

def build_main_system(lang):
    lang_instruction = "Respond entirely in Spanish. All four sections must be in Spanish." if lang == "es" else "Respond in English."
    return f"""You are an expert in emotional abuse dynamics, passive-aggressive and coercive behavior, co-parenting communication, and trauma-informed responses. You help survivors of emotionally abusive relationships process messages from their abusive ex-partners.

{ERICK_CONTEXT}

{lang_instruction}

When given a message from Erick, respond in EXACTLY this format using these exact section headers - no deviations:

===TACTIC===
[One sharp sentence naming the exact manipulation tactic he just used.]

===SAVE===
[YES or NO on the first line. If YES: in 1-2 sentences explain why this message is worth screenshotting and keeping for personal records - e.g. it contains a threat, a false accusation, or a clear behavioral pattern worth remembering. No legal language whatsoever. If NO: write "Nothing to save."]

===RESPONSE1===
[The cathartic response she wishes she could send - for her eyes only, not to send. Name his tactic. Call out the insecurity and projection. Reference his actual track record. Sharp, satisfying, vindicating. Written as Laura speaking in first person.]

===RESPONSE2===
[Grey-rock response to actually send. 1 to 3 sentences MAXIMUM. Logistics only. Zero emotion. Zero JADE. Give him nothing.]"""

def build_olivia_system(lang):
    lang_instruction = "Respond entirely in Spanish. All scripts must be in Spanish." if lang == "es" else "Respond in English."
    return f"""You are a trauma-informed child psychologist specializing in co-parenting and parental alienation. You help mothers respond to their children when those children are in distress during time with a difficult, emotionally unavailable parent.

{ERICK_CONTEXT}

{lang_instruction}

Laura needs actual scripts - things to say to Olivia right now. Not parenting advice. Real sentences a loving mom would say.

The scripts must:
1. Validate Olivia's feelings without badmouthing Erick by name
2. NOT put Olivia in the middle or make her feel responsible for adult decisions
3. NOT rescue Olivia from natural disappointment
4. Help Olivia feel safe, seen, and loved
5. Sound warm and real - not like a therapy textbook
6. Be age-appropriate for an elementary school child

Give exactly 3 scripts. Number them. Each one should be 2-4 sentences."""

def analyze_message(client, lang, message_text=None, image_data=None, extra_context=""):
    system = build_main_system(lang)
    extra = f"\n\nExtra context: {extra_context}" if extra_context.strip() else ""
    if image_data:
        content = [
            {"type": "image", "source": {"type": "base64", "media_type": image_data["media_type"], "data": image_data["data"]}},
            {"type": "text", "text": f"Analyze the message in this screenshot from Erick.{extra}\n\nRespond in the exact format specified."},
        ]
    else:
        content = f"Erick's message:\n\n{message_text}{extra}\n\nRespond in the exact format specified."
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2500,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text

def parse_analysis(raw):
    def extract(tag):
        marker = f"==={tag}==="
        start = raw.find(marker)
        if start == -1:
            return ""
        start += len(marker)
        next_marker = raw.find("===", start)
        return raw[start:next_marker].strip() if next_marker != -1 else raw[start:].strip()
    return {
        "tactic": extract("TACTIC"),
        "save":   extract("SAVE"),
        "r1":     extract("RESPONSE1"),
        "r2":     extract("RESPONSE2"),
    }

def get_olivia_scripts(client, lang, scenario, details=""):
    system = build_olivia_system(lang)
    detail_text = f"\n\nSpecific details: {details}" if details.strip() else ""
    prompt = f"Scenario: {scenario}{detail_text}\n\nGive 3 numbered scripts."
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text

def export_log(log):
    lines = []
    for i, e in enumerate(log, 1):
        lines.append("=" * 60)
        lines.append(f"Entry {i} - {e.get('timestamp','')}")
        lines.append(f"\nHIS MESSAGE:\n{e.get('message','')}")
        lines.append(f"\nTACTIC: {e.get('tactic','')}")
        if e.get("save","").upper().startswith("YES"):
            lines.append(f"\nFLAGGED TO SAVE:\n{e.get('save','')}")
        lines.append(f"\nWHAT SHE WANTED TO SAY:\n{e.get('r1','')}")
        lines.append(f"\nWHAT SHE SENT:\n{e.get('r2','')}")
        lines.append("")
    return "\n".join(lines)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Fuck This Guy", page_icon="🙄", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    font-size: 18px;
    background-color: #ffffff;
}
h1, h2, h3 { color: #1a3a5c; font-weight: 700; }

.subtitle {
    text-align: center; color: #555; font-size: 16px;
    margin-top: -12px; margin-bottom: 24px;
}
.tactic-box {
    background: #fff8e1; border-left: 5px solid #f39c12;
    padding: 14px 20px; border-radius: 8px; margin: 10px 0 16px 0;
    font-size: 16px; color: #333;
}
.legal-yes {
    background: #fff0f0; border-left: 5px solid #e74c3c;
    padding: 14px 20px; border-radius: 8px; margin: 10px 0 16px 0;
    font-size: 16px; color: #333;
}
.legal-no {
    background: #f0fff4; border-left: 5px solid #27ae60;
    padding: 14px 20px; border-radius: 8px; margin: 10px 0 16px 0;
    font-size: 16px; color: #333;
}
.box-fire {
    background: #fff5f5; border-left: 5px solid #c0392b;
    padding: 22px 24px; border-radius: 10px; margin: 10px 0 24px 0;
    font-size: 17px; line-height: 1.7; color: #222;
}
.box-send {
    background: #f0f7ff; border-left: 5px solid #1a3a5c;
    padding: 22px 24px; border-radius: 10px; margin: 10px 0 16px 0;
    font-size: 17px; line-height: 1.7; color: #222;
}
.mood-shield {
    background: linear-gradient(135deg, #1a3a5c 0%, #2a5a8c 100%);
    color: white; padding: 20px 24px; border-radius: 10px; margin: 20px 0 10px 0;
    font-size: 16px; line-height: 1.9;
}
.mood-shield b { color: #ffffff; }
.always-say {
    background: #f8f0ff; border-left: 5px solid #8e44ad;
    padding: 18px 22px; border-radius: 8px; margin: 10px 0 20px 0;
    font-size: 16px; line-height: 2;
}
.olivia-scripts {
    background: #fff9f0; border-left: 5px solid #e67e22;
    padding: 20px 24px; border-radius: 10px; margin: 10px 0 20px 0;
    font-size: 17px; line-height: 1.8; color: #222;
}
.label-tag {
    font-weight: 700; font-size: 15px; letter-spacing: 0.05em;
    margin-bottom: 6px; margin-top: 20px;
}
.stButton > button {
    background-color: #1a3a5c !important; color: white !important;
    font-family: 'Poppins', sans-serif !important; font-size: 17px !important;
    font-weight: 600 !important; padding: 14px 30px !important;
    border-radius: 8px !important; border: none !important;
    width: 100% !important; margin-top: 8px;
}
.stButton > button:hover { background-color: #2a5a8c !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# ── API key gate ──────────────────────────────────────────────────────────────
api_key = load_key()
if not api_key or not api_key.startswith("sk-ant-"):
    st.markdown("<h1 style='text-align:center;'>🙄 Fuck This Guy</h1>", unsafe_allow_html=True)
    st.divider()
    st.warning("One-time setup: paste your Anthropic API key to get started.")
    key_input = st.text_input("Your Anthropic API key:", type="password", placeholder="sk-ant-api03-...")
    if st.button("Save & Continue"):
        if key_input.strip().startswith("sk-ant-"):
            save_key(key_input)
            st.success("Key saved. Refresh the page.")
            st.stop()
        else:
            st.error("Key should start with sk-ant-")
    st.stop()

client = Anthropic(api_key=api_key)

# ── Language toggle ───────────────────────────────────────────────────────────
col_spacer, col_toggle = st.columns([3, 1])
with col_toggle:
    lang_choice = st.radio("", ["🇺🇸 English", "🇪🇸 Español"],
        index=0 if st.session_state.lang == "en" else 1,
        horizontal=False, label_visibility="collapsed")
    st.session_state.lang = "en" if "English" in lang_choice else "es"

lang = st.session_state.lang

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;'>🙄 Fuck This Guy</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{t('subtitle')}</div>", unsafe_allow_html=True)
st.caption(t("disclaimer"))
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_main, tab_olivia, tab_log = st.tabs([t("tab_messages"), t("tab_olivia"), t("tab_log")])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — HIS MESSAGES
# ═════════════════════════════════════════════════════════════════════════════
with tab_main:
    with st.expander(t("context_expander")):
        extra_context = st.text_area(t("context_label"), height=90, placeholder=t("context_ph"))

    st.markdown(t("msg_header"))
    t1, t2 = st.tabs([t("tab_paste"), t("tab_screenshot")])
    message_text_input = ""
    uploaded_file = None

    with t1:
        message_text_input = st.text_area(t("paste_label"), height=150, placeholder=t("paste_ph"))
    with t2:
        uploaded_file = st.file_uploader(t("upload_label"), type=["png", "jpg", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)

    if st.button(t("analyze_btn"), key="analyze"):
        has_text = bool(message_text_input and message_text_input.strip())
        has_image = uploaded_file is not None

        if not has_text and not has_image:
            st.error(t("error_no_input"))
        else:
            with st.spinner(t("spinner_analyze")):
                try:
                    if has_image:
                        raw_bytes = uploaded_file.read()
                        b64 = base64.standard_b64encode(raw_bytes).decode("utf-8")
                        image_data = {"data": b64, "media_type": uploaded_file.type or "image/png"}
                        raw = analyze_message(client, lang, image_data=image_data, extra_context=extra_context or "")
                    else:
                        raw = analyze_message(client, lang, message_text=message_text_input, extra_context=extra_context or "")

                    parsed = parse_analysis(raw)
                    st.divider()

                    st.markdown(f"<div class='label-tag' style='color:#f39c12;'>{t('tactic_label')}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='tactic-box'>{parsed['tactic']}</div>", unsafe_allow_html=True)

                    if parsed["save"].upper().startswith("YES"):
                        st.markdown(f"<div class='label-tag' style='color:#f39c12;'>{t('save_label')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='tactic-box'>{parsed['save']}</div>", unsafe_allow_html=True)

                    st.markdown(f"<div class='label-tag' style='color:#c0392b;'>{t('r1_label')}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='box-fire'>{parsed['r1'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

                    st.markdown(f"<div class='label-tag' style='color:#1a3a5c;'>{t('r2_label')}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='box-send'>{parsed['r2'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    st.text_area(t("copy_label"), value=parsed["r2"], height=90, key="copy_r2")

                    st.markdown(f"""
<div class='mood-shield'>
<b>{t('mood_title')}</b><br><br>
{t('mood_body')}<br><br>
<em>{t('mood_closing')}</em>
</div>""", unsafe_allow_html=True)

                    save_log_entry({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "message": message_text_input if has_text else "[screenshot]",
                        "tactic": parsed["tactic"],
                        "save": parsed["save"],
                        "r1": parsed["r1"],
                        "r2": parsed["r2"],
                    })

                except Exception as e:
                    st.error(f"{t('error_generic')} {e}")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — OLIVIA MODE
# ═════════════════════════════════════════════════════════════════════════════
with tab_olivia:
    st.markdown(t("olivia_header"))
    st.markdown(t("olivia_sub"))

    st.markdown(f"<div class='label-tag' style='color:#8e44ad;'>{t('always_label')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='always-say'>{t('always_phrases')}</div>", unsafe_allow_html=True)
    st.divider()

    st.markdown(t("scripts_header"))
    scenario = st.selectbox(t("scenario_label"), t("scenarios"))
    details = st.text_area(t("details_label"), height=90, placeholder=t("details_ph"))

    if st.button(t("olivia_btn"), key="olivia"):
        with st.spinner(t("spinner_olivia")):
            try:
                scripts = get_olivia_scripts(client, lang, scenario, details)
                st.markdown(f"<div class='label-tag' style='color:#e67e22;'>{t('scripts_label')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='olivia-scripts'>{scripts.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"{t('error_generic')} {e}")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — LOG
# ═════════════════════════════════════════════════════════════════════════════
with tab_log:
    log = load_log()
    st.markdown(f"### {t('log_header')} - {len(log)} entries")

    if not log:
        st.info(t("log_empty"))
    else:
        export_text = export_log(log)
        st.download_button(
            label=t("export_btn"),
            data=export_text,
            file_name=f"erick_communications_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )
        st.divider()

        for entry in log:
            with st.expander(f"📅 {entry.get('timestamp','')} - {entry.get('tactic','')[:60]}..."):
                st.markdown(f"**{t('log_his_msg')}** {entry.get('message','')}")
                st.markdown(f"**{t('log_tactic')}** {entry.get('tactic','')}")
                saved = entry.get("save", "")
                if saved.upper().startswith("YES"):
                    st.markdown(f"**📸 {t('log_save')}** {saved}")
                st.markdown(f"**{t('log_sent')}** {entry.get('r2','')}")

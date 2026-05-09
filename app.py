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

# ── AI context ────────────────────────────────────────────────────────────────

ERICK_CONTEXT = """
You are analyzing messages from Erick, the ex-husband of Laura.

Known patterns about Erick:
- Tells Laura she is a "bad mom" because she trains for elite athletic competitions (Ironman races, Leadville 100 invitee — invitation only). His logic: watching football on the couch is "good parenting" because he's present, but her training is bad parenting because she has to leave.
- During his own custody weeks, he sits on the couch while their daughter Olivia plays alone or on a tablet all day. Zero engagement.
- He blames Laura whenever Olivia gets a normal childhood illness ("she always gets sick on your watch"), despite his complete non-engagement when he has her.
- He wouldn't let Laura display her hundreds of race medals — a normal athlete tradition — controlling her achievements even in their shared home.
- He has been fired from multiple jobs (at least 3). He tells people at work that everything gets dumped on him and he saves the day. He almost certainly underperforms.
- He is significantly less educated, motivated, and intellectually capable than Laura, who is a successful attorney with a stable career throughout their marriage and after.
- He has very few friends. Refuses therapy. Is homophobic and judgmental.
- During his own custody weeks, he regularly dumps Olivia back on Laura claiming he's "too busy with work" — then doesn't engage when he does have her.
- He has eroded Laura's confidence so thoroughly that she now questions her own good decisions.
- Core dynamic: deeply insecure, threatened by Laura's competence, social life, achievements, and independence. Tears her down to feel better about himself. Uses Olivia as a weapon to wound Laura.
- Psychological profile: NOT classic narcissism. Closer to covert passive-aggressive personality with fragile ego, victim mentality, and compensatory control behaviors. Projects his failures onto Laura.

Laura's actual profile:
- Successful attorney, steady employment throughout their marriage and after
- Elite endurance athlete — Ironman finisher, Leadville 100 invitee (invitation only, elite athletes only)
- Hundreds of race medals
- Highly social, widely liked, active, engaged, loving mother
- Has been systematically undermined by Erick until she questions her own judgment
- Daughter: Olivia (elementary school age)
"""

MAIN_SYSTEM = f"""You are an expert in emotional abuse dynamics, passive-aggressive and coercive behavior, co-parenting communication, and trauma-informed responses. You help survivors of emotionally abusive relationships process messages from their abusive ex-partners.

{ERICK_CONTEXT}

When given a message from Erick, respond in EXACTLY this format using these exact section headers — no deviations:

===TACTIC===
[One sharp sentence naming the exact manipulation tactic he just used. Examples: "He used guilt inversion — reframing his failure to parent as evidence of your moral failure." or "He used blame-shifting — turning a routine childhood illness into an indictment of your parenting." Be specific and name the tactic clearly.]

===LEGAL===
[Start with YES or NO on the first line. If YES: explain what this message demonstrates, why it is legally significant (custody violation, coercive communication, parental alienation, pattern evidence, etc.), and what Laura should do — screenshot, note date/time, forward to attorney. If NO: write exactly "Nothing to flag legally."]

===RESPONSE1===
[The cathartic response she wishes she could send — for her eyes only, not to send. Name his tactic explicitly. Call out the insecurity and projection behind what he said. Be sharp, satisfying, and vindicating. Reference his actual track record where relevant — the job losses, the couch parenting, the medals he wouldn't let her display, the custody weeks he dumps on her. Written as Laura speaking in first person. End with something that grounds her — reminds her she sees him clearly and she is not the problem.]

===RESPONSE2===
[Grey-rock response to actually send. 1 to 3 sentences MAXIMUM. Address only logistics related to Olivia. Zero emotion. Zero JADE (Justify, Argue, Defend, Explain). Give him absolutely nothing to feed on. What a trauma-informed therapist or divorce coach would recommend.]"""

OLIVIA_SYSTEM = f"""You are a trauma-informed child psychologist specializing in co-parenting and parental alienation. You help mothers respond to their children when those children are in distress during time with a difficult, emotionally unavailable parent.

{ERICK_CONTEXT}

Laura needs actual scripts — things to say to Olivia right now. Not parenting advice. Real sentences a loving mom would say.

The scripts must:
1. Validate Olivia's feelings without badmouthing Erick by name
2. NOT put Olivia in the middle or make her feel responsible for adult decisions
3. NOT rescue Olivia from natural disappointment (that teaches resilience and holds Erick accountable)
4. Help Olivia feel safe, seen, and loved
5. Sound warm and real — not like a therapy textbook
6. Be age-appropriate for an elementary school child

Give exactly 3 scripts. Number them. Each one should be 2-4 sentences."""


def analyze_message(client, message_text=None, image_data=None, extra_context=""):
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
        system=MAIN_SYSTEM,
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
        "legal": extract("LEGAL"),
        "r1": extract("RESPONSE1"),
        "r2": extract("RESPONSE2"),
    }


def get_olivia_scripts(client, scenario, details=""):
    detail_text = f"\n\nSpecific details Laura shared: {details}" if details.strip() else ""
    prompt = f"Scenario: {scenario}{detail_text}\n\nGive Laura 3 numbered scripts — actual things to say to Olivia right now."
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1000,
        system=OLIVIA_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def export_log(log):
    lines = []
    for i, e in enumerate(log, 1):
        lines.append(f"{'='*60}")
        lines.append(f"Entry {i} — {e.get('timestamp','')}")
        lines.append(f"\nHIS MESSAGE:\n{e.get('message','')}")
        lines.append(f"\nTACTIC: {e.get('tactic','')}")
        lines.append(f"\nLEGAL FLAG:\n{e.get('legal','')}")
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
    font-weight: 700; font-size: 14px; letter-spacing: 0.05em;
    margin-bottom: 6px; margin-top: 20px;
}
.log-entry {
    border: 1px solid #e0e0e0; border-radius: 8px;
    padding: 16px 18px; margin-bottom: 14px; font-size: 15px;
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
            st.error("That doesn't look right — key should start with sk-ant-")
    st.stop()

client = Anthropic(api_key=api_key)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;'>🙄 Fuck This Guy</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>His messages, decoded. Olivia, protected. Laura, restored.</div>", unsafe_allow_html=True)
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_main, tab_olivia, tab_log = st.tabs(["💬 His Messages", "💛 Olivia Mode", "📋 Log"])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — HIS MESSAGES
# ═════════════════════════════════════════════════════════════════════════════
with tab_main:
    with st.expander("Add context about this specific message (optional)"):
        extra_context = st.text_area(
            "Anything that helps — time of day, what triggered it, what happened before:",
            height=90,
            placeholder="E.g. 'He sent this at 11pm after I told him I was running a race this weekend'",
        )

    st.markdown("### His message")
    t1, t2 = st.tabs(["Paste text", "Upload screenshot"])
    message_text_input = ""
    uploaded_file = None

    with t1:
        message_text_input = st.text_area("Paste his text or email:", height=150, placeholder="Paste exactly what he said...")
    with t2:
        uploaded_file = st.file_uploader("Upload a screenshot:", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)

    if st.button("Analyze & Get Responses", key="analyze"):
        has_text = bool(message_text_input and message_text_input.strip())
        has_image = uploaded_file is not None

        if not has_text and not has_image:
            st.error("Paste his message or upload a screenshot first.")
        else:
            with st.spinner("Reading between his lines..."):
                try:
                    if has_image:
                        raw_bytes = uploaded_file.read()
                        b64 = base64.standard_b64encode(raw_bytes).decode("utf-8")
                        image_data = {"data": b64, "media_type": uploaded_file.type or "image/png"}
                        raw = analyze_message(client, image_data=image_data, extra_context=extra_context or "")
                    else:
                        raw = analyze_message(client, message_text=message_text_input, extra_context=extra_context or "")

                    parsed = parse_analysis(raw)
                    st.divider()

                    # ── Tactic Decoder ────────────────────────────────────
                    st.markdown("<div class='label-tag' style='color:#f39c12;'>🎯 WHAT HE JUST DID</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='tactic-box'>{parsed['tactic']}</div>", unsafe_allow_html=True)

                    # ── Legal Flag ────────────────────────────────────────
                    legal_text = parsed["legal"]
                    is_legal_yes = legal_text.upper().startswith("YES")
                    if is_legal_yes:
                        st.markdown("<div class='label-tag' style='color:#e74c3c;'>⚖️ LEGAL FLAG — DOCUMENT THIS</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='legal-yes'>{legal_text}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='label-tag' style='color:#27ae60;'>⚖️ LEGAL FLAG</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='legal-no'>{legal_text}</div>", unsafe_allow_html=True)

                    # ── Response 1 ────────────────────────────────────────
                    st.markdown("<div class='label-tag' style='color:#c0392b;'>🔥 WHAT YOU REALLY WANT TO SAY — do not send</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='box-fire'>{parsed['r1'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

                    # ── Response 2 ────────────────────────────────────────
                    st.markdown("<div class='label-tag' style='color:#1a3a5c;'>💙 WHAT TO ACTUALLY SEND</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='box-send'>{parsed['r2'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    st.text_area("Copy to send:", value=parsed["r2"], height=90, key="copy_r2")

                    # ── Mood Shield ───────────────────────────────────────
                    st.markdown("""
<div class='mood-shield'>
<b>Before you send that — remember who you actually are:</b><br><br>
🏅 &nbsp;Ironman finisher. Multiple races.<br>
🏔️ &nbsp;Leadville 100 invitee — <em>invitation only</em>. Elite athletes only.<br>
🥇 &nbsp;Hundreds of race medals.<br>
⚖️ &nbsp;Successful attorney. Steady career. Never been fired.<br>
👯 &nbsp;Surrounded by real friends. Well-traveled. Fully alive.<br>
💛 &nbsp;A mother who actually shows up.<br><br>
<em>Send Response 2 from that person. Not from who he says you are.</em>
</div>
""", unsafe_allow_html=True)

                    # ── Save to log ───────────────────────────────────────
                    save_log_entry({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "message": message_text_input if has_text else "[screenshot]",
                        "tactic": parsed["tactic"],
                        "legal": parsed["legal"],
                        "r1": parsed["r1"],
                        "r2": parsed["r2"],
                    })

                except Exception as e:
                    st.error(f"Something went wrong: {e}")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — OLIVIA MODE
# ═════════════════════════════════════════════════════════════════════════════
with tab_olivia:
    st.markdown("### What to say to Olivia")
    st.markdown("Use this when she calls crying during his week, or when she comes home upset.")

    # Always-say phrases — always visible
    st.markdown("<div class='label-tag' style='color:#8e44ad;'>💜 PHRASES LAURA CAN ALWAYS SAY — no matter what happened</div>", unsafe_allow_html=True)
    st.markdown("""
<div class='always-say'>
&nbsp;• &nbsp;"I love you so much, and that will never ever change."<br>
&nbsp;• &nbsp;"Your feelings make complete sense. It's okay to feel sad / mad / disappointed."<br>
&nbsp;• &nbsp;"You didn't do anything wrong. This is not your fault."<br>
&nbsp;• &nbsp;"Grown-up stuff is never your job to fix."<br>
&nbsp;• &nbsp;"I'm always here when you need me."<br>
&nbsp;• &nbsp;"You are such a strong kid and I am so proud of you."
</div>
""", unsafe_allow_html=True)

    st.divider()

    # Scenario-specific scripts
    st.markdown("### Get scripts for right now")
    scenario = st.selectbox("What's happening?", [
        "He won't take her to gymnastics or an activity",
        "He won't take her to a birthday party or social event",
        "He yelled at her or she's scared of him",
        "She's crying and begging mom to come fix it",
        "She says dad said something mean or unfair",
        "She's asking why daddy doesn't do things with her",
        "She's had a hard week with him and just got home",
        "He's being cold or ignoring her",
        "She's asking why mom and dad aren't together",
    ])

    details = st.text_area("Any specific details? (optional — makes the scripts sharper):",
        height=90,
        placeholder="E.g. 'She called crying because he said he had too much work and couldn't take her to gymnastics. She's been looking forward to it all week.'")

    if st.button("Get Scripts for Olivia", key="olivia"):
        with st.spinner("Getting the right words..."):
            try:
                scripts = get_olivia_scripts(client, scenario, details)
                st.markdown("<div class='label-tag' style='color:#e67e22;'>💬 WHAT LAURA CAN SAY TO OLIVIA RIGHT NOW</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='olivia-scripts'>{scripts.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — COMMUNICATION LOG
# ═════════════════════════════════════════════════════════════════════════════
with tab_log:
    log = load_log()
    st.markdown(f"### Communication Log — {len(log)} entries")

    if not log:
        st.info("No messages analyzed yet. Your log will appear here after you use the His Messages tab.")
    else:
        export_text = export_log(log)
        st.download_button(
            label="⬇️ Export Full Log (for your attorney)",
            data=export_text,
            file_name=f"erick_communications_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )
        st.divider()

        for entry in log:
            with st.expander(f"📅 {entry.get('timestamp','')} — {entry.get('tactic','')[:60]}..."):
                st.markdown(f"**His message:** {entry.get('message','')}")
                st.markdown(f"**Tactic:** {entry.get('tactic','')}")
                legal = entry.get('legal','')
                if legal.upper().startswith("YES"):
                    st.markdown(f"**⚖️ Legal flag:** {legal}")
                st.markdown(f"**What she sent:** {entry.get('r2','')}")

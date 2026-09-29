import json
import streamlit as st
import agent, memory

st.set_page_config(
    page_title="NetNest Support AI (Hindsight Memory)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS Theme
def load_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        pass

load_css()

# Session State Initialization
if "story_complete" not in st.session_state:
    st.session_state.story_complete = False

# PHASE 1: CINEMATIC INTRO
query_params = st.query_params
if query_params.get("skip_story") == "1":
    st.session_state.story_complete = True

if not st.session_state.story_complete:
    import intro_ui
    header, skip = st.columns([5, 1], vertical_alignment="center")
    with header:
        st.markdown("<div style='color:#00E5FF; font-weight:800; font-size:14px; letter-spacing:.15em;'>NETNEST / SUPPORT THAT REMEMBERS</div>", unsafe_allow_html=True)
    with skip:
        if st.button("Skip to demo ↗", type="secondary", key="skip_intro_btn"):
            st.session_state.story_complete = True
            st.rerun()
    intro_ui.render_cinematic_intro()
    st.stop()

# PHASE 2: LIVE DEMO APP
_v3_data = json.load(open("seed_data_v3.json"))
customers = {
    cid: f"{info['name']} — {info['description'].split(';')[0]}"
    for cid, info in _v3_data.items()
}

ss = st.session_state
ss.setdefault("chats", {})
ss.setdefault("scores", {})
ss.setdefault("briefs", {})

# Hindsight Memory Caching
@st.cache_data(ttl=30, show_spinner=False)
def load_profile(cid):
    return memory.get_profile(cid)

@st.cache_data(ttl=30, show_spinner=False)
def load_beliefs(cid):
    return memory.list_observations(cid, 8)

@st.cache_data(ttl=30, show_spinner=False)
def load_recent(cid):
    try:
        items = memory.list_memories(cid, limit=100).items
        items = sorted(items, key=lambda m: m.mentioned_at or "", reverse=True)
        return [m.text.split(" | ")[0] for m in items[:10]], len(items)
    except Exception as e:
        return [], 0

# SIDEBAR: CUSTOMER SELECTOR & MEMORY PANEL
with st.sidebar:
    st.markdown("### ⚡ NetNest Support AI")
    st.caption("Powered by Hindsight Persistent Memory")
    st.divider()

    cid = st.selectbox("Customer Profile", list(customers), format_func=lambda k: customers[k])
    use_memory = st.toggle("Memory ON", value=True, help="Toggle OFF to test generic tier-1 responses with zero customer memory.")
    st.divider()

    if not use_memory:
        st.warning("⚠️ **Memory is OFF**. The agent has no access to past tickets or troubleshooting history for this customer.")
    else:
        st.subheader("📋 Customer Profile")
        try:
            profile = load_profile(cid)
            if profile:
                st.markdown("\n".join(l for l in profile.splitlines() if not l.startswith("#")))
            else:
                st.caption("Profile is being written by Hindsight...")
        except Exception as e:
            st.caption(f"Couldn't load profile: {e}")

        st.subheader("💡 What the Agent Believes")
        try:
            beliefs = load_beliefs(cid)
            if beliefs:
                st.caption("Consolidated by Hindsight from past tickets:")
                for b in beliefs:
                    st.markdown(f"- {b}")
            else:
                st.caption("No consolidated beliefs yet.")
        except Exception as e:
            st.caption(f"Couldn't load beliefs: {e}")

        with st.expander("📜 Raw Memories (Newest First)"):
            try:
                recent, total = load_recent(cid)
                st.caption(f"{total} stored memories in bank")
                for r in recent:
                    st.markdown(f"- {r}")
            except Exception as e:
                st.caption(f"Couldn't load memories: {e}")

# MAIN CHATBOT DEMO AREA
name = customers[cid]
st.title("NetNest Support Agent")
st.caption(f"Chatting as: **{name}**")

# Scenario Details & Test Prompt Chips
CUSTOMER_HINTS = {
    "cust-bre-v3": {
        "scenario": "Breanna's connection drops repeatedly. App says fine, modem offline, phone line says outage. Doesn't want to cancel Saturday technician.",
        "chips": [
            "Why does the phone line say outage but your app says normal?",
            "Will my Saturday technician visit still happen?",
            "My internet dropped again for the 4th time today!"
        ]
    },
    "cust-gavin-v3": {
        "scenario": "Gavin is tech-savvy with a Motorola SB6121. Flashing blue Send light = upstream bonding issue. Already power-cycled everything.",
        "chips": [
            "My Motorola SB6121 has a flashing blue Send light.",
            "I already power cycled modem and router, is it upstream bonding?",
            "Can you check signal levels on my upstream channels?"
        ]
    },
    "cust-jordan-v3": {
        "scenario": "Jordan faces SSN verification mismatches activating a $9/mo extra TV box. Packaged the device to return.",
        "chips": [
            "SSN verification failed when activating my $9 TV box.",
            "I already packed the box to send back to you.",
            "Why do I need SSN verification for an extra receiver?"
        ]
    }
}

hint = CUSTOMER_HINTS.get(cid, {})

# Memory State Banner
if use_memory:
    st.info("🧠 **MEMORY ACTIVE:** Agent recalls past tickets, skips failed modem reboots, and personalizes solutions.")
else:
    st.warning("⚠️ **MEMORY OFF:** Generic tier-1 agent. Asks to reboot modem and verify basic account info.")

# Scenario & Suggested Prompt Chips
if hint.get("scenario"):
    st.caption(f"💡 **Scenario Context:** {hint['scenario']}")

if hint.get("chips"):
    st.caption("Suggested Prompt Chips (Click to test agent memory):")
    chip_cols = st.columns(len(hint["chips"]))
    for idx, chip_text in enumerate(hint["chips"]):
        if chip_cols[idx].button(f"💬 {chip_text}", key=f"chip_btn_{cid}_{idx}"):
            ss["preset_prompt"] = chip_text

# Escalated Human Handoff Banner
if cid in ss.briefs:
    st.error("🚨 **AUTOMATED HUMAN HANDOFF TRIGGERED** (Frustration >= 4 on consecutive turns)")
    st.markdown("**Hindsight Reflect Case Brief:**")
    st.info(ss.briefs[cid])

# Render Chat History Stream
chat = ss.chats.setdefault(cid, [])
for m in chat:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if "used" in m:
            st.caption(f"✨ Recalled {m['used']} memories · Frustration: {m['score']}/5")

# Handle Chat Input & Preset Prompts
preset_prompt = ss.pop("preset_prompt", None)
prompt = st.chat_input("Type as the customer...")
if preset_prompt and not prompt:
    prompt = preset_prompt

if prompt:
    history = list(chat)
    chat.append({"role": "user", "content": prompt})
    with st.spinner("Agent is thinking & querying Hindsight memory..."):
        reply, score, facts = agent.respond(cid, name, prompt, history, use_memory)
    chat.append({"role": "assistant", "content": reply, "used": len(facts), "score": score})

    scores = ss.scores.setdefault(cid, [])
    scores.append(score)
    if use_memory and len(scores) >= 2 and scores[-1] >= 4 and scores[-2] >= 4 and cid not in ss.briefs:
        try:
            ss.briefs[cid] = memory.reflect(
                cid, "Write a short handoff brief for a human support agent: who the customer is, "
                     "what has been tried, what worked or failed, and their current mood. Under 120 words.")
        except Exception as e:
            ss.briefs[cid] = f"(Could not generate brief: {e})"

    st.cache_data.clear()
    st.rerun()

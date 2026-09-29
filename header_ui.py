"""Header & Customer Selector Component for NetNest Streamlit App.
Provides avatar cards for customer selection, scenario hints with prompt chips,
and the liquid Memory ON/OFF toggle bar.
"""

import streamlit as st

CUSTOMER_DETAILS = {
    "cust-bre-v3": {
        "name": "Bre",
        "full_name": "Breanna Miller",
        "avatar": "👩🏽‍💻",
        "color": "#00E5FF",
        "desc": "Chronic repeat connection drops; conflicting outage info; Saturday tech visit.",
        "scenario": "Bre's connection drops repeatedly. App says fine, modem offline, phone line says outage. She doesn't want to cancel her Saturday technician visit.",
        "chips": [
            "Why does the phone line say outage but your app says normal?",
            "Will my Saturday technician visit still happen?",
            "My internet dropped again for the 4th time today!"
        ]
    },
    "cust-gavin-v3": {
        "name": "Gavin",
        "full_name": "Gavin Vance",
        "avatar": "👨🏼‍🔧",
        "color": "#7C3AED",
        "desc": "Tech-savvy; Motorola SB6121; flashing blue Send light (upstream bonding).",
        "scenario": "Gavin is tech-savvy with a Motorola SB6121. Flashing blue Send light indicates upstream bonding issue. He has already power-cycled everything.",
        "chips": [
            "My Motorola SB6121 has a flashing blue Send light.",
            "I already power cycled modem and router, is it upstream bonding?",
            "Can you check signal levels on my upstream channels?"
        ]
    },
    "cust-jordan-v3": {
        "name": "Jordan",
        "full_name": "Jordan Lee",
        "avatar": "🧑🏻‍💼",
        "color": "#FF2E93",
        "desc": "SSN verification mismatch activating $9/mo TV box; device packaged to return.",
        "scenario": "Jordan faces SSN verification mismatches while activating a $9/month extra TV box. Highly frustrated, Jordan has already packaged the device to return.",
        "chips": [
            "SSN verification failed when activating my $9 TV box.",
            "I already packed the box to send back to you.",
            "Why do I need SSN verification for a simple extra TV box?"
        ]
    }
}

def render_header():
    ss = st.session_state
    
    # Top Brand Bar & Navigation Controls
    col_brand, col_toggle = st.columns([2.5, 1.5], vertical_alignment="center")
    
    with col_brand:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 38px; height: 38px; border-radius: 12px; background: linear-gradient(135deg, #00E5FF, #7C3AED); display: grid; place-items: center; font-weight: 900; font-size: 20px; box-shadow: 0 0 20px rgba(0,229,255,0.4);">⚡</div>
            <div>
                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 22px; font-weight: 800; letter-spacing: -0.02em; color: #FFFFFF;">
                    NETNEST <span style="font-size: 13px; font-weight: 600; color: #00E5FF; padding: 2px 8px; border-radius: 20px; background: rgba(0,229,255,0.1); border: 1px solid rgba(0,229,255,0.3);">HINDSIGHT MEMORY</span>
                </div>
                <div style="font-size: 12px; color: #94A3B8;">Broadband & Cable Support AI Agent</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_toggle:
        memory_on = st.toggle("🧠 Memory ON", value=ss.get("use_memory", True), key="use_memory_toggle")
        ss["use_memory"] = memory_on

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Customer Selector Avatar Cards
    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3]
    
    current_cid = ss.get("selected_cid", "cust-bre-v3")
    
    for i, (cid, info) in enumerate(CUSTOMER_DETAILS.items()):
        is_selected = (cid == current_cid)
        with cols[i]:
            card_class = "customer-card active" if is_selected else "customer-card"
            st.markdown(f"""
            <div class="{card_class}">
                <div class="customer-avatar" style="border-color: {info['color']};">
                    {info['avatar']}
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 15px; color: #FFFFFF; display: flex; align-items: center; justify-content: space-between;">
                        {info['name']}
                        {f"<span style='font-size:10px; color:{info['color']}; background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:10px;'>ACTIVE</span>" if is_selected else ""}
                    </div>
                    <div style="font-size: 11.5px; color: #94A3B8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {info['desc']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Select {info['name']}", key=f"btn_cust_{cid}"):
                ss["selected_cid"] = cid
                st.rerun()

    # Scenario Hint & Clickable Prompt Chips
    selected_info = CUSTOMER_DETAILS.get(current_cid, CUSTOMER_DETAILS["cust-bre-v3"])
    
    st.markdown(f"""
    <div class="scenario-box">
        <div class="scenario-hint-text">
            💡 <strong>Scenario Hint ({selected_info['full_name']}):</strong> {selected_info['scenario']}
        </div>
        <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Suggested Prompt Chips (Click to test agent memory):</div>
    </div>
    """, unsafe_allow_html=True)

    # Render Prompt Chips as Buttons
    chip_cols = st.columns(len(selected_info['chips']))
    for idx, chip_text in enumerate(selected_info['chips']):
        with chip_cols[idx]:
            if st.button(f"💬 {chip_text}", key=f"chip_{current_cid}_{idx}"):
                ss["preset_prompt"] = chip_text
                st.rerun()

    # Side-by-side Compare Hint Banner
    use_mem = ss.get("use_memory", True)
    if use_mem:
        st.markdown("""
        <div style="padding: 10px 16px; background: rgba(0, 229, 255, 0.08); border: 1px solid rgba(0, 229, 255, 0.25); border-radius: 12px; font-size: 12.5px; color: #00E5FF; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            <span>🧠 <strong>MEMORY ACTIVE:</strong> Agent recalls past tickets, skips failed modem reboots, and personalizes solutions.</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding: 10px 16px; background: rgba(255, 59, 48, 0.08); border: 1px solid rgba(255, 59, 48, 0.25); border-radius: 12px; font-size: 12.5px; color: #FF3B30; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
            <span>⚠️ <strong>MEMORY OFF:</strong> Agent acts as generic tier-1 support. It has zero knowledge of past tickets and will repeat basic reboot steps.</span>
        </div>
        """, unsafe_allow_html=True)

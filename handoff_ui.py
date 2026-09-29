"""Frustration Gauge & Human Handoff Modal Component for NetNest Streamlit App.
Tracks customer frustration levels (1-5), displays visual arc gauge,
pulses screen edges on escalation, and renders stylized Handoff Brief Case File.
"""

import streamlit as st

def render_frustration_gauge(current_score: int):
    emojis = {1: "🟢 😊", 2: "🟢 🙂", 3: "🟡 😐", 4: "🟧 😠", 5: "🔴 🤬"}
    labels = {1: "Calm", 2: "Relaxed", 3: "Moderate", 4: "Frustrated", 5: "Furious"}
    
    score_color = "#B6FF3B" if current_score <= 2 else ("#FFD700" if current_score == 3 else "#FF2E93")
    shake_class = "lvl-4" if current_score >= 4 else "lvl-1"

    st.markdown(f"""
    <div class="frustration-gauge-container">
        <div class="frustration-level-dot {shake_class}" style="background: {score_color}; box-shadow: 0 0 10px {score_color};"></div>
        <div style="font-size: 13px; font-weight: 700; color: #FFFFFF; font-family: 'Space Grotesk', sans-serif;">
            Frustration Meter: <span style="color: {score_color};">{current_score}/5</span> ({labels.get(current_score, 'Normal')}) {emojis.get(current_score, '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_handoff_brief_modal(cid: str, brief_text: str):
    if not brief_text:
        return

    st.markdown(f"""
    <div class="escalation-pulse-active"></div>
    <div class="handoff-modal-overlay">
        <div class="handoff-modal-card">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <div class="case-file-badge">⚠️ AUTOMATED HUMAN HANDOFF TRIGGERED</div>
                <div style="font-size: 12px; color: #FF2E93; font-weight: 700;">HINDSIGHT REFLECT SUMMARY</div>
            </div>
            
            <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 800; margin-bottom: 8px; color: #FFFFFF;">
                Connecting Customer to Tier-2 Specialist
            </h2>
            <p style="font-size: 13.5px; color: #94A3B8; margin-bottom: 18px;">
                Frustration reached 4+ on consecutive turns. Hindsight generated the following case brief so the agent has 100% context instantly without asking the customer to repeat.
            </p>

            <div style="background: #060412; border: 1px dashed #FF2E93; border-radius: 14px; padding: 18px; margin-bottom: 20px; font-family: 'Inter', sans-serif; font-size: 14px; line-height: 1.6; color: #F1F5F9;">
                <div style="font-size: 11px; font-weight: 700; color: #FF2E93; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
                    📁 CASE BRIEF FILE (HINDSIGHT REFLECT):
                </div>
                {brief_text}
            </div>

            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 12px; color: #94A3B8;">
                    ✓ Case file saved to Hindsight Memory Bank
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

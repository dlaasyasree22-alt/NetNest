"""Live Memory Sidebar Component for NetNest Streamlit App.
Provides tabbed views for Customer Profile (Mental Model), Consolidated Beliefs/Observations,
Raw Memory Terminal Timeline, and an interactive SVG Memory Node Graph.
"""

import streamlit as st

def render_memory_sidebar(cid: str, profile_text: str, beliefs: list[str], raw_memories: list[str], total_raw: int, use_memory: bool = True):
    ss = st.session_state
    
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
            🧠 <span>HINDSIGHT MEMORY PANEL</span>
        </div>
        <div style="font-size: 11px; background: rgba(0,229,255,0.1); border: 1px solid rgba(0,229,255,0.3); color: #00E5FF; padding: 2px 8px; border-radius: 12px; font-weight: 600;">
            LIVE SYNC
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not use_memory:
        st.markdown("""
        <div style="padding: 24px 18px; background: rgba(255,59,48,0.08); border: 1px solid rgba(255,59,48,0.25); border-radius: 18px; text-align: center;">
            <div style="font-size: 32px; margin-bottom: 8px;">🧠❌</div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 15px; color: #FF3B30; margin-bottom: 6px;">Memory is OFF</div>
            <div style="font-size: 12.5px; color: #94A3B8; line-height: 1.5;">
                The agent currently has no access to past tickets, mental models, or consolidated customer beliefs.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Memory Node Graph (SVG Canvas Visualization)
    st.markdown("""
    <div style="background: rgba(10, 8, 26, 0.7); border: 1px solid rgba(0,229,255,0.2); border-radius: 16px; padding: 12px; margin-bottom: 16px;">
        <div style="font-size: 11.5px; font-weight: 700; color: #00E5FF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
            <span>Memory Graph Nodes</span>
            <span style="font-size: 10px; color: #94A3B8;">Hindsight Vector Topology</span>
        </div>
        <svg viewBox="0 0 300 80" style="width: 100%; height: 70px;">
            <line x1="30" y1="40" x2="90" y2="20" stroke="#7C3AED" stroke-width="1.5" stroke-dasharray="3,3"/>
            <line x1="90" y1="20" x2="160" y2="55" stroke="#00E5FF" stroke-width="2"/>
            <line x1="160" y1="55" x2="220" y2="25" stroke="#FF2E93" stroke-width="1.5"/>
            <line x1="220" y1="25" x2="270" y2="45" stroke="#B6FF3B" stroke-width="2"/>

            <circle cx="30" cy="40" r="6" fill="#7C3AED"><animate attributeName="r" values="5;7;5" dur="3s" repeatCount="indefinite"/></circle>
            <circle cx="90" cy="20" r="8" fill="#00E5FF"><animate attributeName="r" values="7;9;7" dur="2s" repeatCount="indefinite"/></circle>
            <circle cx="160" cy="55" r="7" fill="#FF2E93"><animate attributeName="r" values="6;8;6" dur="2.5s" repeatCount="indefinite"/></circle>
            <circle cx="220" cy="25" r="8" fill="#B6FF3B"><animate attributeName="r" values="7;10;7" dur="3.5s" repeatCount="indefinite"/></circle>
            <circle cx="270" cy="45" r="5" fill="#00E5FF"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # Active Tab Selector
    active_tab = ss.get("sidebar_active_tab", "profile")
    
    t1, t2, t3 = st.columns(3)
    with t1:
        if st.button("📋 Profile", key="tab_btn_profile"):
            ss["sidebar_active_tab"] = "profile"
            st.rerun()
    with t2:
        if st.button("💡 Beliefs", key="tab_btn_beliefs"):
            ss["sidebar_active_tab"] = "beliefs"
            st.rerun()
    with t3:
        if st.button("📜 Raw Logs", key="tab_btn_raw"):
            ss["sidebar_active_tab"] = "raw"
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # TAB 1: PROFILE (Mental Model)
    if active_tab == "profile":
        clean_profile = "\n".join(l for l in profile_text.splitlines() if not l.startswith("#")) if profile_text else ""
        if not clean_profile:
            clean_profile = "Mental model is actively being constructed by Hindsight from incoming memories..."
        
        st.markdown(f"""
        <div class="profile-doc-box">
            <div style="font-size: 11px; font-weight: 700; color: #00E5FF; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                <span>Mental Model Document</span>
                <span style="font-size: 10px; color: #B6FF3B;">+1 Memory Retained</span>
            </div>
            <div style="white-space: pre-wrap; font-size: 13px; line-height: 1.6; color: #E2E8F0;">
                {clean_profile}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # TAB 2: BELIEFS / OBSERVATIONS
    elif active_tab == "beliefs":
        st.markdown("""
        <div style="font-size: 11.5px; color: #94A3B8; margin-bottom: 12px;">
            Consolidated beliefs synthesized by Hindsight from past support turns:
        </div>
        """, unsafe_allow_html=True)
        
        if not beliefs:
            st.markdown("<div style='font-size:12.5px; color:#64748B;'>No consolidated beliefs extracted yet.</div>", unsafe_allow_html=True)
        else:
            for idx, belief in enumerate(beliefs):
                conf_val = 85 - (idx * 6)
                st.markdown(f"""
                <div class="belief-card">
                    <div style="font-size: 13px; font-weight: 600; color: #F8FAFC; display: flex; align-items: flex-start; gap: 8px;">
                        <span>🔹</span>
                        <div>{belief}</div>
                    </div>
                    <div class="confidence-bar-bg">
                        <div class="confidence-bar-fill" style="width: {conf_val}%;"></div>
                    </div>
                    <div style="font-size: 10px; color: #94A3B8; text-align: right; margin-top: 4px;">
                        Confidence: {conf_val}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # TAB 3: RAW MEMORY TIMELINE
    elif active_tab == "raw":
        st.markdown(f"""
        <div style="font-size: 11.5px; color: #94A3B8; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
            <span>Timeline Log (Newest First)</span>
            <span style="color: #00E5FF; font-weight: 600;">{total_raw} stored</span>
        </div>
        <div class="terminal-logs">
        """, unsafe_allow_html=True)
        
        if not raw_memories:
            st.markdown("<div style='color:#64748B;'>[0 items found]</div>", unsafe_allow_html=True)
        else:
            for mem in raw_memories:
                st.markdown(f"""
                <div style="margin-bottom: 8px; border-bottom: 1px dashed rgba(255,255,255,0.06); padding-bottom: 6px;">
                    <span style="color: #FF2E93; font-weight: 600;">&gt;</span> {mem}
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("</div>", unsafe_allow_html=True)

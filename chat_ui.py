"""Real-Time Chat UI Component for NetNest Streamlit App.
Provides the animated conversation stream, bot avatar, Thinking Orb,
border beam wrappers, memory-recalled chips, and chat input.
"""

import streamlit as st

AVATARS = {
    "cust-bre-v3": {"name": "Bre", "avatar": "👩🏽‍💻", "color": "#00E5FF"},
    "cust-gavin-v3": {"name": "Gavin", "avatar": "👨🏼‍🔧", "color": "#7C3AED"},
    "cust-jordan-v3": {"name": "Jordan", "avatar": "🧑🏻‍💼", "color": "#FF2E93"},
}

def render_thinking_orb(use_memory: bool = True):
    mode_class = "" if use_memory else "memory-off-mode"
    st.markdown(f"""
    <div class="{mode_class}">
        <div class="thinking-orb-wrapper">
            <div class="thinking-orb"></div>
            <div>
                <div class="thinking-status-text" id="thinking-status">Thinking & Analyzing...</div>
                <div style="font-size: 11px; color: #94A3B8;">Hindsight Persistent Context Engine</div>
            </div>
        </div>
    </div>
    <script>
        (function() {{
            const statuses = [
                "Recalling past tickets...",
                "Searching customer mental model...",
                "Skipping failed reboot steps...",
                "Reflecting on frustration signals..."
            ];
            let idx = 0;
            const el = document.getElementById('thinking-status');
            if (el) {{
                setInterval(() => {{
                    idx = (idx + 1) % statuses.length;
                    el.textContent = statuses[idx];
                }}, 1200);
            }}
        }})();
    </script>
    """, unsafe_allow_html=True)

def render_chat_stream(cid: str, chat_history: list[dict], use_memory: bool = True):
    customer_info = AVATARS.get(cid, {"name": "Customer", "avatar": "👤", "color": "#00E5FF"})
    mode_class = "" if use_memory else "memory-off-mode"
    
    st.markdown(f"""
    <div class="{mode_class}">
        <div class="border-beam-container">
            <div class="border-beam-content" style="padding: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #00E5FF, #7C3AED); display: grid; place-items: center; font-size: 18px; box-shadow: 0 0 15px rgba(0,229,255,0.4);">
                            🤖
                        </div>
                        <div>
                            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 15px; color: #FFFFFF;">
                                NetNest Support AI
                            </div>
                            <div style="font-size: 11.5px; color: #94A3B8;">
                                Chatting with {customer_info['name']}
                            </div>
                        </div>
                    </div>
                    <div style="font-size: 12px; color: #94A3B8; display: flex; align-items: center; gap: 6px;">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: {'#00E5FF' if use_memory else '#FF3B30'}; display: inline-block;"></span>
                        {'Memory Active' if use_memory else 'Generic Mode'}
                    </div>
                </div>

                <div class="chat-container" id="chat-messages-box">
    """, unsafe_allow_html=True)

    if not chat_history:
        st.markdown(f"""
        <div style="text-align: center; padding: 40px 20px; color: #64748B;">
            <div style="font-size: 32px; margin-bottom: 8px;">💬</div>
            <div style="font-weight: 600; font-size: 14px; color: #94A3B8;">No conversation history yet.</div>
            <div style="font-size: 12px;">Type a message below or click a suggested prompt chip above.</div>
        </div>
        """, unsafe_allow_html=True)

    for msg in chat_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        used_count = msg.get("used", 0)
        score = msg.get("score", None)

        if role == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 14px;">
                <div class="chat-bubble chat-bubble-user">
                    <div style="font-size: 10.5px; opacity: 0.8; margin-bottom: 4px; font-weight: 700;">{customer_info['name']}</div>
                    <div>{content}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            memory_chip_html = ""
            if use_memory and used_count > 0:
                memory_chip_html = f"""
                <div class="memory-chip-tag">
                    ✨ Recalled {used_count} memory facts & skipped failed steps
                </div>
                """
            elif not use_memory:
                memory_chip_html = """
                <div style="display: inline-flex; align-items: center; gap: 6px; margin-top: 8px; padding: 4px 10px; background: rgba(255,59,48,0.1); border: 1px solid rgba(255,59,48,0.3); border-radius: 20px; font-size: 11px; color: #FF3B30;">
                    ⚠️ Memory OFF: Generic tier-1 answer (no past ticket recall)
                </div>
                """

            frustration_badge = ""
            if score is not None:
                score_color = "#B6FF3B" if score <= 2 else ("#FFD700" if score == 3 else "#FF2E93")
                frustration_badge = f"""
                <span style="font-size: 11px; color: {score_color}; margin-left: 8px; font-weight: 600;">
                    (Frustration: {score}/5)
                </span>
                """

            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 14px;">
                <div class="chat-bubble chat-bubble-agent">
                    <div style="font-size: 10.5px; color: #00E5FF; margin-bottom: 4px; font-weight: 700; display: flex; align-items: center;">
                        🤖 NetNest Support AI {frustration_badge}
                    </div>
                    <div>{content}</div>
                    {memory_chip_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
                </div>
            </div>
        </div>
    </div>
    <script>
        // Auto scroll to bottom
        const box = document.getElementById('chat-messages-box');
        if (box) { box.scrollTop = box.scrollHeight; }
    </script>
    """, unsafe_allow_html=True)

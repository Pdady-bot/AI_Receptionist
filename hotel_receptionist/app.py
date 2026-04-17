"""
app.py  ← Run with:  streamlit run app.py
------
Hotel AI Receptionist — Main Streamlit Application

STRUCTURE:
    1. Page config & CSS styling
    2. Session state initialization (chat history, reservations)
    3. Sidebar — hotel info + quick action buttons
    4. Main chat interface
    5. Message handling & AI response
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
from ai.ai_receptionist import get_ai_response
from data.hotel_data import HOTEL_INFO, ROOM_TYPES, init_reservations

# ══════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Azure Grand — AI Receptionist",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — luxury hotel aesthetic ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=Jost:wght@300;400;500&display=swap');

/* Overall font */
html, body, [class*="css"] {
    font-family: 'Jost', sans-serif;
}

/* Page background */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0f1a 100%);
}

/* Hotel name header */
.hotel-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 300;
    color: #c9a96e;
    letter-spacing: 0.15em;
    text-align: center;
    margin-bottom: 0.1rem;
}
.hotel-tagline {
    font-size: 0.7rem;
    color: #666;
    text-align: center;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* Chat message bubbles */
.user-bubble {
    background: linear-gradient(135deg, #1a3a5c, #1e4976);
    color: #e8f4fd;
    padding: 0.85rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    margin: 0.4rem 0 0.4rem 3rem;
    font-size: 0.92rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.ai-bubble {
    background: linear-gradient(135deg, #1a1a24, #1e1e2e);
    color: #ddd;
    padding: 0.85rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    margin: 0.4rem 3rem 0.4rem 0;
    font-size: 0.92rem;
    line-height: 1.6;
    border-left: 3px solid #c9a96e;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

/* Aria avatar label */
.aria-label {
    font-size: 0.7rem;
    color: #c9a96e;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
    margin-left: 0.2rem;
}
.user-label {
    font-size: 0.7rem;
    color: #5a8ab8;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    text-align: right;
    margin-bottom: 0.2rem;
    margin-right: 0.2rem;
}

/* Room card in sidebar */
.room-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(201,169,110,0.2);
    border-radius: 8px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.82rem;
}
.room-name {
    color: #c9a96e;
    font-weight: 500;
    margin-bottom: 0.2rem;
}
.room-price {
    color: #aaa;
    font-size: 0.78rem;
}

/* Divider line */
.gold-divider {
    border: none;
    border-top: 1px solid rgba(201,169,110,0.3);
    margin: 1rem 0;
}

/* Quick action buttons */
.stButton > button {
    background: rgba(201,169,110,0.1) !important;
    color: #c9a96e !important;
    border: 1px solid rgba(201,169,110,0.3) !important;
    border-radius: 6px !important;
    font-family: 'Jost', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(201,169,110,0.2) !important;
    border-color: #c9a96e !important;
}

/* Chat input */
.stChatInput > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(201,169,110,0.3) !important;
    border-radius: 12px !important;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080810 0%, #0d0d1a 100%) !important;
    border-right: 1px solid rgba(201,169,110,0.15) !important;
}

/* Remove default streamlit styling */
.block-container { padding-top: 1.5rem; }

/* Mobile responsive */
@media (max-width: 768px) {
    .hotel-name {
        font-size: 1.2rem !important;
    }
    .ai-bubble, .user-bubble {
        margin-left: 0.5rem !important;
        margin-right: 0.5rem !important;
        font-size: 0.85rem !important;
    }
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 2. SESSION STATE INITIALIZATION
#    Session state = variables that persist between reruns
#    Every time user sends a message, Streamlit reruns the whole script
#    Without session state, the chat history would disappear each time
# ══════════════════════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    # Start with a greeting from Aria
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                f"Welcome to **{HOTEL_INFO['name']}**. 🏨\n\n"
                "I'm **Aria**, your personal AI concierge. I'm here to help you with:\n\n"
                "• 🛏️ **Room reservations** — booking, checking, modifying or cancelling\n"
                "• ❓ **Hotel information** — WiFi, amenities, dining, spa and more\n"
                "• 📍 **Local attractions** — personalised recommendations nearby\n\n"
                "How may I assist you today?"
            )
        }
    ]

# Initialize reservations storage
init_reservations()


# ══════════════════════════════════════════════════════════════════════════════
# 3. SIDEBAR — Hotel Info Panel
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="hotel-name">AZURE GRAND</div>', unsafe_allow_html=True)
    st.markdown('<div class="hotel-tagline">Sydney • Est. 1987</div>', unsafe_allow_html=True)
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

    # ── Quick info ────────────────────────────────────────────────────────────
    st.markdown("##### 🕐 Hotel Hours")
    st.caption(f"Check-in: **{HOTEL_INFO['check_in_time']}**  |  Check-out: **{HOTEL_INFO['check_out_time']}**")
    st.caption(f"🍽️ {HOTEL_INFO['restaurant']}")
    st.caption(f"🍸 {HOTEL_INFO['bar']}")
    st.caption(f"🏊 Pool: {HOTEL_INFO['pool_hours']}")

    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

    # ── Room types ────────────────────────────────────────────────────────────
    st.markdown("##### 🛏️ Available Rooms")
    for room_name, details in ROOM_TYPES.items():
        st.markdown(f"""
        <div class="room-card">
            <div class="room-name">{room_name}</div>
            <div class="room-price">${details['price_per_night']}/night · {details['beds']} · {details['view']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

    # ── Quick action buttons ──────────────────────────────────────────────────
    # These inject a pre-written message into the chat when clicked
    st.markdown("##### ⚡ Quick Actions")

    if st.button("📅 Make a Reservation"):
        st.session_state.quick_message = "I'd like to make a room reservation."
    if st.button("🔍 Check My Booking"):
        st.session_state.quick_message = "I'd like to check my existing reservation."
    if st.button("❌ Cancel Reservation"):
        st.session_state.quick_message = "I need to cancel my reservation."
    if st.button("📍 Local Attractions"):
        st.session_state.quick_message = "What are some local attractions near the hotel?"
    if st.button("ℹ️ Hotel Amenities"):
        st.session_state.quick_message = "Tell me about the hotel amenities."
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = [st.session_state.messages[0]]  # Keep greeting
        st.rerun()

    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

    # ── My Reservations panel ─────────────────────────────────────────────────
    st.markdown("##### 📋 My Reservations")
    reservations = st.session_state.get("reservations", {})
    confirmed = {k: v for k, v in reservations.items() if v["status"] == "confirmed"}

    if confirmed:
        for bid, b in list(confirmed.items())[:3]:  # Show max 3
            st.markdown(f"""
            <div class="room-card">
                <div class="room-name">#{b['booking_id']}</div>
                <div class="room-price">{b['room_type']}<br>{b['check_in']} → {b['check_out']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No active reservations")


# ══════════════════════════════════════════════════════════════════════════════
# 4. MAIN CHAT INTERFACE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="hotel-name" style="font-size:1.4rem; margin-bottom:0; text-align:center; width:100%">THE AZURE GRAND</div>', unsafe_allow_html=True)
st.markdown('<div class="hotel-tagline" style="margin-bottom:1rem">AI CONCIERGE · ARIA</div>', unsafe_allow_html=True)

# ── Render all existing messages ──────────────────────────────────────────────
# Loop through conversation history and display each message
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown('<div class="aria-label">✦ Aria</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-bubble">{message["content"]}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="user-label">You</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-bubble">{message["content"]}</div>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 5. HANDLE INPUT — both typed messages and quick action buttons
# ══════════════════════════════════════════════════════════════════════════════

# Check if a quick action button was pressed
# If so, use that as the user input
user_input = None

if "quick_message" in st.session_state and st.session_state.quick_message:
    user_input = st.session_state.quick_message
    st.session_state.quick_message = None   # Clear it so it doesn't repeat

# Chat input box at the bottom
chat_input = st.chat_input("Ask Aria anything about your stay...")
if chat_input:
    user_input = chat_input


# ── Process the user message ──────────────────────────────────────────────────
if user_input:
    # 1. Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown('<div class="user-label">You</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)

    # 2. Show a spinner while waiting for AI response
    with st.spinner("Aria is typing..."):
        # Build messages list for API (exclude the initial greeting's system context)
        # Only send role/content pairs — no extra keys
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # 3. Get AI response from Claude
        response = get_ai_response(api_messages)

    # 4. Add response to history and display it
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown('<div class="aria-label">✦ Aria</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-bubble">{response}</div>', unsafe_allow_html=True)

    # 5. Rerun to refresh sidebar (e.g. update reservations panel)
    st.rerun()

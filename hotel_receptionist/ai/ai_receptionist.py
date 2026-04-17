"""
ai_receptionist.py
------------------
This is the AI brain of the app.
It sends the guest's message to Groq API and gets a smart response back.

HOW IT WORKS:
1. Guest types a message
2. We build a "system prompt" telling Groq it's a hotel receptionist
3. We send the full conversation history + new message Groq API
4. Groq replies naturally, using the hotel info we gave it
5. We display the reply in the chat

KEY CONCEPT — System Prompt:
    The system prompt is a set of instructions given to Groq before the
    conversation starts. It tells Groq WHO it is, WHAT it knows, and
    HOW to behave. Think of it like a staff briefing before a shift.
"""

from groq import Groq
import streamlit as st
import json
from data.hotel_data import (
    HOTEL_INFO, ROOM_TYPES, LOCAL_ATTRACTIONS,
    make_reservation, get_reservation,
    cancel_reservation, modify_reservation
)


def build_system_prompt() -> str:
    """
    Builds the instruction set for Groq.
    We inject all hotel data directly into the prompt so Groq
    knows everything about the hotel without needing a database query.
    """

    # Format room types nicely for the prompt
    rooms_text = ""
    for room_name, details in ROOM_TYPES.items():
        rooms_text += f"""
    - {room_name}: ${details['price_per_night']}/night, {details['beds']},
      {details['view']}, sleeps {details['capacity']},
      Amenities: {', '.join(details['amenities'])}"""

    # Format attractions
    attractions_text = ""
    for a in LOCAL_ATTRACTIONS:
        attractions_text += f"\n    - {a['name']} ({a['distance']}) — {a['tip']}"

    return f"""You are Aria, the friendly and professional AI receptionist for {HOTEL_INFO['name']}.
You help guests with reservations, answer questions about the hotel, and recommend local attractions.

HOTEL INFORMATION:
- Name: {HOTEL_INFO['name']}
- Location: {HOTEL_INFO['location']}
- Check-in: {HOTEL_INFO['check_in_time']} | Check-out: {HOTEL_INFO['check_out_time']}
- WiFi Network: {HOTEL_INFO['wifi_network']} | Password: {HOTEL_INFO['wifi_password']}
- Parking: {HOTEL_INFO['parking']}
- Pool: {HOTEL_INFO['pool_hours']}
- Gym: {HOTEL_INFO['gym_hours']}
- Restaurant: {HOTEL_INFO['restaurant']}
- Bar: {HOTEL_INFO['bar']}
- Spa: {HOTEL_INFO['spa']}
- Pet Policy: {HOTEL_INFO['pet_policy']}
- Cancellation Policy: {HOTEL_INFO['cancellation_policy']}

AVAILABLE ROOMS:
{rooms_text}

LOCAL ATTRACTIONS NEARBY:
{attractions_text}

YOUR CAPABILITIES:
1. Answer any hotel FAQ questions
2. Help guests BOOK a room — collect: guest name, room type, check-in date, check-out date, number of guests
3. Help guests CHECK a reservation — ask for their booking ID
4. Help guests CANCEL a reservation — ask for booking ID, confirm before cancelling
5. Help guests MODIFY dates — ask for booking ID and new dates
6. Recommend local attractions based on guest interests

BOOKING INSTRUCTIONS:
- When a guest wants to book, collect ALL required details conversationally
- Once you have all details, output EXACTLY this JSON block (and nothing before it on that line):
  BOOKING_ACTION:{{"action":"book","guest_name":"...","room_type":"...","check_in":"YYYY-MM-DD","check_out":"YYYY-MM-DD","guests":2}}

- When a guest wants to check/lookup a booking:
  BOOKING_ACTION:{{"action":"check","booking_id":"..."}}

- When a guest wants to cancel:
  BOOKING_ACTION:{{"action":"cancel","booking_id":"..."}}

- When a guest wants to modify dates:
  BOOKING_ACTION:{{"action":"modify","booking_id":"...","new_check_in":"YYYY-MM-DD","new_check_out":"YYYY-MM-DD"}}

PERSONALITY & TONE:
- Warm, professional, and welcoming — like a 5-star hotel receptionist
- Use the guest's name once you know it
- Be concise but friendly
- Use light formatting (bullet points for lists, bold for important info)
- Always end with an offer to help further
- Never make up information not provided above
"""


def process_booking_action(action_json: str) -> str:
    """
    Parses the BOOKING_ACTION JSON from Groq's response
    and executes the actual reservation operation.
    Returns a result message to inject back to Groq.
    """
    try:
        data = json.loads(action_json)
        action = data.get("action")

        if action == "book":
            booking = make_reservation(
                guest_name = data["guest_name"],
                room_type  = data["room_type"],
                check_in   = data["check_in"],
                check_out  = data["check_out"],
                guests     = data["guests"],
            )
            return (f"BOOKING_CONFIRMED: Booking ID {booking['booking_id']} created. "
                    f"Guest: {booking['guest_name']}, Room: {booking['room_type']}, "
                    f"Check-in: {booking['check_in']}, Check-out: {booking['check_out']}, "
                    f"Nights: {booking['nights']}, Total: ${booking['total_price']}")

        elif action == "check":
            booking = get_reservation(data["booking_id"])
            if booking:
                return (f"BOOKING_FOUND: ID {booking['booking_id']}, "
                        f"Guest: {booking['guest_name']}, Room: {booking['room_type']}, "
                        f"Check-in: {booking['check_in']}, Check-out: {booking['check_out']}, "
                        f"Status: {booking['status']}, Total: ${booking['total_price']}")
            else:
                return f"BOOKING_NOT_FOUND: No reservation found with ID {data['booking_id']}"

        elif action == "cancel":
            success = cancel_reservation(data["booking_id"])
            if success:
                return f"BOOKING_CANCELLED: Reservation {data['booking_id']} has been cancelled."
            else:
                return f"BOOKING_NOT_FOUND: No reservation found with ID {data['booking_id']}"

        elif action == "modify":
            booking = modify_reservation(
                data["booking_id"], data["new_check_in"], data["new_check_out"]
            )
            if booking:
                return (f"BOOKING_MODIFIED: Reservation {booking['booking_id']} updated. "
                        f"New dates: {booking['check_in']} to {booking['check_out']}, "
                        f"Nights: {booking['nights']}, New total: ${booking['total_price']}")
            else:
                return f"BOOKING_NOT_FOUND: No reservation found with ID {data['booking_id']}"

    except Exception as e:
        return f"BOOKING_ERROR: {str(e)}"


def get_ai_response(messages: list) -> str:
    """
    Sends the conversation to Groq API and returns the response.

    Args:
        messages - list of {"role": "user"/"assistant", "content": "..."} dicts
                   This is the full conversation history

    Returns:
        The AI's response as a string
    """
    # Initialize the Groq client
    # It automatically uses the Groq_API_KEY environment variable
    client = Groq()

    try:
        response = client.chat.completions.create(
            model      = "openai/gpt-oss-120b",   
            max_tokens = 1024,
            messages   = [{"role": "system",  "content": build_system_prompt()}] + messages,     # Full conversation history
        )

        reply = response.choices[0].message.content

        # ── CHECK IF Groq WANTS TO PERFORM A BOOKING ACTION ─────────────────
        # Groq signals an action by including "BOOKING_ACTION:{...}" in its reply
        if "BOOKING_ACTION:" in reply:
            # Split at the action marker
            parts = reply.split("BOOKING_ACTION:")
            pre_text    = parts[0].strip()   # Text before the action
            action_json = parts[1].strip()   # The JSON action data

            # Execute the booking operation
            action_result = process_booking_action(action_json)

            # Send result back to Groq so it can respond naturally to the guest
            # We add the result as a user message and get a follow-up response
            follow_up_messages = messages + [
                {"role": "assistant", "content": reply},
                {"role": "user",      "content": f"SYSTEM_RESULT: {action_result}. "
                                                  "Please respond to the guest naturally with this result, "
                                                  "confirming the action in a friendly way."},
            ]
            follow_up = client.chat.completions.create(
                model      = "openai/gpt-oss-120b",
                max_tokens = 1024,                
                messages   = [{"role": "system", "content": build_system_prompt()}]+follow_up_messages,
            )
            return follow_up.choices[0].message.content

        return reply

    except Exception as e:
        if "auth" in str(e).lower():
            return ("API Key issue set your groq api key")
            
        return f"Something went wrong: {str(e)}"

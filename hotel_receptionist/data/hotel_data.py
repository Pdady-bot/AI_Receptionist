"""
hotel_data.py
-------------
All hotel information and reservation management.
Think of this as the hotel's database.
In a real project this would connect to an actual database (PostgreSQL, Firebase etc.)
For now we use Python dictionaries stored in Streamlit's session state.
"""

# ── HOTEL PROFILE ─────────────────────────────────────────────────────────────
HOTEL_INFO = {
    "name": "The Azure Grand Hotel",
    "location": "123 Oceanview Boulevard, Sydney, Australia",
    "phone": "+61 2 9000 1234",
    "email": "reservations@azuregrand.com",
    "check_in_time": "3:00 PM",
    "check_out_time": "11:00 AM",
    "wifi_password": "AzureGuest2024",
    "wifi_network": "AzureGrand_Guest",
    "parking": "Complimentary valet parking available 24/7",
    "pool_hours": "6:00 AM – 10:00 PM daily",
    "gym_hours": "24 hours",
    "restaurant": "The Coral Restaurant — Open 7:00 AM to 10:30 PM",
    "bar": "The Blue Lounge — Open 12:00 PM to 1:00 AM",
    "spa": "Azure Spa — Open 9:00 AM to 8:00 PM, booking recommended",
    "concierge": "Available 24/7 at the front desk or dial 0 from your room",
    "pet_policy": "We are a pet-friendly hotel. Pets under 10kg welcome. $30/night pet fee.",
    "cancellation_policy": "Free cancellation up to 48 hours before check-in. After that, one night's fee applies.",
}

# ── ROOM TYPES ────────────────────────────────────────────────────────────────
ROOM_TYPES = {
    "Standard Room": {
        "price_per_night": 180,
        "capacity": 2,
        "beds": "1 Queen Bed",
        "view": "City View",
        "amenities": ["Free WiFi", "Air conditioning", "Flat-screen TV", "Mini fridge", "Room service"],
        "available": 8,
    },
    "Deluxe Ocean Room": {
        "price_per_night": 280,
        "capacity": 2,
        "beds": "1 King Bed",
        "view": "Ocean View",
        "amenities": ["Free WiFi", "Air conditioning", "Flat-screen TV", "Mini bar", "Balcony", "Room service", "Bathrobe & slippers"],
        "available": 5,
    },
    "Family Suite": {
        "price_per_night": 380,
        "capacity": 4,
        "beds": "1 King Bed + 2 Single Beds",
        "view": "Garden View",
        "amenities": ["Free WiFi", "Air conditioning", "2 Flat-screen TVs", "Full kitchen", "Living area", "Room service"],
        "available": 3,
    },
    "Penthouse Suite": {
        "price_per_night": 650,
        "capacity": 2,
        "beds": "1 Super King Bed",
        "view": "Panoramic Ocean View",
        "amenities": ["Free WiFi", "Air conditioning", "Smart TV", "Full bar", "Private terrace", "Butler service", "Jacuzzi", "Premium toiletries"],
        "available": 1,
    },
}

# ── LOCAL ATTRACTIONS ─────────────────────────────────────────────────────────
LOCAL_ATTRACTIONS = [
    {"name": "Sydney Opera House",      "distance": "10 min walk",  "type": "Landmark",     "tip": "Book evening performances in advance"},
    {"name": "Bondi Beach",             "distance": "20 min drive", "type": "Beach",        "tip": "Best surfing early morning"},
    {"name": "The Rocks Markets",       "distance": "15 min walk",  "type": "Shopping",     "tip": "Open Saturday & Sunday 10am-5pm"},
    {"name": "Taronga Zoo",             "distance": "30 min ferry", "type": "Family",       "tip": "Ferry from Circular Quay is part of the experience"},
    {"name": "Royal Botanic Garden",    "distance": "5 min walk",   "type": "Nature",       "tip": "Free entry, beautiful harbour views"},
    {"name": "Darling Harbour",         "distance": "25 min walk",  "type": "Dining/Entertainment", "tip": "Great for dinner and waterfront strolls"},
    {"name": "Blue Mountains",          "distance": "2 hr drive",   "type": "Nature",       "tip": "Book a day tour from the hotel concierge"},
    {"name": "Sydney Harbour Bridge",   "distance": "15 min walk",  "type": "Landmark",     "tip": "BridgeClimb offers unforgettable views"},
]


# ── RESERVATION FUNCTIONS ─────────────────────────────────────────────────────
import streamlit as st
import random
import string
from datetime import datetime

def generate_booking_id() -> str:
    """Creates a random 8-character booking reference like 'AZ-X7K2M9'"""
    chars = string.ascii_uppercase + string.digits
    return "AZ-" + "".join(random.choices(chars, k=6))


def init_reservations():
    """
    Initialize the reservations storage in Streamlit session state.
    Session state persists data while the app is running (like a temporary database).
    We use a dictionary: { booking_id: booking_details }
    """
    if "reservations" not in st.session_state:
        # Add a sample existing booking so users can test the 'check booking' feature
        st.session_state.reservations = {
            "AZ-SAMPLE": {
                "booking_id":   "AZ-SAMPLE",
                "guest_name":   "John Smith",
                "room_type":    "Deluxe Ocean Room",
                "check_in":     "2024-12-20",
                "check_out":    "2024-12-23",
                "guests":       2,
                "total_price":  840,
                "status":       "confirmed",
                "created_at":   "2024-11-01",
            }
        }


def make_reservation(guest_name: str, room_type: str,
                     check_in: str, check_out: str, guests: int) -> dict:
    """
    Creates a new reservation and saves it to session state.
    Returns the booking details dictionary.
    """
    init_reservations()

    # Calculate number of nights and total price
    fmt         = "%Y-%m-%d"
    nights      = (datetime.strptime(check_out, fmt) - datetime.strptime(check_in, fmt)).days
    price_night = ROOM_TYPES[room_type]["price_per_night"]
    total       = nights * price_night

    booking = {
        "booking_id":  generate_booking_id(),
        "guest_name":  guest_name,
        "room_type":   room_type,
        "check_in":    check_in,
        "check_out":   check_out,
        "guests":      guests,
        "nights":      nights,
        "total_price": total,
        "status":      "confirmed",
        "created_at":  datetime.now().strftime("%Y-%m-%d"),
    }

    st.session_state.reservations[booking["booking_id"]] = booking
    return booking


def get_reservation(booking_id: str):
    """Look up a reservation by booking ID. Returns None if not found."""
    init_reservations()
    return st.session_state.reservations.get(booking_id.upper(), None)


def cancel_reservation(booking_id: str) -> bool:
    """
    Cancels a reservation by marking its status as 'cancelled'.
    Returns True if found and cancelled, False if not found.
    """
    init_reservations()
    booking_id = booking_id.upper()
    if booking_id in st.session_state.reservations:
        st.session_state.reservations[booking_id]["status"] = "cancelled"
        return True
    return False


def modify_reservation(booking_id: str, new_check_in: str, new_check_out: str):
    """
    Updates check-in/check-out dates and recalculates total price.
    Returns updated booking or None if not found.
    """
    init_reservations()
    booking_id = booking_id.upper()
    if booking_id not in st.session_state.reservations:
        return None

    booking     = st.session_state.reservations[booking_id]
    fmt         = "%Y-%m-%d"
    nights      = (datetime.strptime(new_check_out, fmt) - datetime.strptime(new_check_in, fmt)).days
    price_night = ROOM_TYPES[booking["room_type"]]["price_per_night"]

    booking["check_in"]    = new_check_in
    booking["check_out"]   = new_check_out
    booking["nights"]      = nights
    booking["total_price"] = nights * price_night
    return booking

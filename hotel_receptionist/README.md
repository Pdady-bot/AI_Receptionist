# 🏨 Azure Grand — AI Hotel Receptionist

A conversational AI receptionist for a luxury hotel, powered by Groq.
Built with Streamlit for the chat interface.

---

## 📁 Project Structure

```
hotel_receptionist/
│
├── app.py                    ← MAIN FILE — run this
│
├── ai/
│   └── ai_receptionist.py   ← Claude API integration + booking logic
│
├── data/
│   └── hotel_data.py        ← Hotel info, room types, reservation functions
│
└── requirements.txt
```

---

## 🚀 How to Run

### Step 1 — Install packages
```bash
pip install -r requirements.txt
```

### Step 2 — Set your Groq API key
```bash
# Mac/Linux:
export GROQ_API_KEY=your_key_here

# Windows (Command Prompt):
set  GROQ_API_KEY=your_key_here

# Windows (PowerShell):
$env: GROQ_API_KEY="your_key_here"
```


### Step 3 — Run the app
```bash
streamlit run app.py
```

---

## 💬 What Aria Can Do

- **Book rooms** — collects name, room type, dates, guests and confirms
- **Check reservations** — look up any booking by ID
- **Cancel bookings** — with confirmation
- **Modify dates** — updates and recalculates total price
- **Hotel FAQs** — WiFi, check-in/out, pool, gym, restaurant, spa, parking
- **Local attractions** — Sydney Opera House, Bondi Beach, and more

## 🧪 Test Booking ID
Use **AZ-SAMPLE** to test the check/cancel/modify features

---

## 🔧 Customising for Real Use

To adapt for a real hotel:
1. Edit `data/hotel_data.py` — update `HOTEL_INFO`, `ROOM_TYPES`, `LOCAL_ATTRACTIONS`
2. Replace session state storage with a real database (PostgreSQL, Firebase etc.)
3. Add email confirmation using `smtplib` or SendGrid

---

## 🛠️ Tech Stack
- **Streamlit** — web interface
- ** GROQ API** — AI responses
- **Python** — backend logic

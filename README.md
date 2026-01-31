🫀 JeevSetu
AI-Powered Emergency Organ Donation & Matching Platform

SDG-3: Good Health & Well-Being

📌 Overview

OrganMatch is a smart, emergency-focused organ donation coordination platform that uses AI-based ranking, real-time geolocation, and secure identity verification to drastically reduce delays in organ allocation.

Unlike traditional static registries, OrganMatch actively responds to emergencies by prioritizing urgency, compatibility, and distance, ensuring faster life-saving decisions.

🎯 Problem Statement

Organ allocation is slow, manual, and fragmented

Lack of real-time donor availability

No distance or ETA awareness

High risk of fraud or identity mismatch

Poor hospital–patient coordination

⏱ In emergencies, minutes matter — delays cost lives.

💡 Solution

JeevSetu provides:

🚨 SOS Emergency Trigger

🤖 AI-based Donor Ranking

📍 Live Google Maps Integration

🏥 Hospital & Admin Dashboards

🪪 DigiLocker-based Identity Verification

📊 Analytics & Monitoring

🧠 Key Features
👤 User Dashboard

Search organs & hospitals

Visual organ cards

Emergency SOS button

Google Maps hospital navigation

📸 Screenshot:


🚨 Emergency SOS System

Location-based nearest hospital detection

Distance & ETA calculation

Immediate matching

📸 Screenshot:


🏥 Hospital Dashboard

Manage donor availability

Update organ status

Respond to SOS requests

📸 Screenshot:


🛠 Admin Dashboard

System analytics

User & hospital monitoring

Emergency logs

Decision transparency

📸 Screenshot:


🤖 AI Matching Logic

The system ranks donors using a weighted scoring model:

Final Score =
  (Organ Compatibility × Weight)
+ (Urgency Level × Weight)
− (Geographical Distance)


📍 Distance is calculated using the Haversine Formula
🏆 Highest score = Best match

🗺 Google Maps Integration

Live hospital locations

Route navigation

Distance & ETA

Emergency routing


🧰 Tech Stack
Frontend

Streamlit (Rapid UI Prototyping)

HTML + CSS (Custom Styling)

Backend

Python

Flask-style routing logic

REST-based architecture

Database

SQLite (Prototype)

PostgreSQL (Production-ready design)

APIs & Tools

Google Maps

DigiLocker (OAuth – planned)

AI/ML ranking engine

🏗 Architecture
User / Hospital / Admin
        ↓
   Frontend UI
        ↓
 Matching Engine (AI)
        ↓
 Database + Geo Logic
        ↓
 Google Maps / Analytics

🌍 SDG Alignment

SDG-3: Good Health & Well-Being

✔ Emergency healthcare access
✔ Reduced preventable deaths
✔ Digital public health infrastructure

🚀 How to Run
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py


Open browser at:

http://localhost:8501

🔮 Future Enhancements

Live ambulance tracking

Deep ML model using transplant history

Blockchain audit trails

Mobile application

National organ registry integration

👥 Team

Team Kaizen
Innovation for Impact 🚀

🏁 Conclusion

JeevSetu is not just a project — it is a life-saving digital health solution.
Built for emergencies, designed for scale, and aligned with national healthcare goals.



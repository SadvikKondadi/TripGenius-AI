# TripGenius AI 🌍✈️

AI-powered smart travel planner built using **React, FastAPI, Gemini AI, Neo4j AuraDB, and Pexels API**.

TripGenius AI dynamically generates personalized travel itineraries, destination-specific recommendations, hotel suggestions, budget breakdowns, and travel images for any location in the world.

---

# 🚀 Live Demo

## Frontend (Vercel)

https://trip-genius-ai-rouge.vercel.app

## Backend API (Render)

https://tripgenius-ai-backend.onrender.com

---

# ✨ Features

- 🌎 Plan trips for any destination worldwide
- 🤖 AI-generated personalized itineraries using Gemini AI
- 🏨 Hotel & accommodation recommendations
- 💰 Budget breakdown & travel cost estimation
- 🍜 Food recommendations based on user preference
- 🖼 Dynamic destination images using Pexels API
- 🗺 Day-wise itinerary generation
- 🧠 Neo4j graph database integration
- 💾 Search history & trip graph relationships
- 📱 Responsive modern UI/UX
- ☁️ Fully deployed using Vercel + Render

---

# 🛠 Tech Stack

## Frontend
- React.js
- Vite
- CSS3
- Axios

## Backend
- FastAPI
- Python
- Gemini AI API
- Neo4j AuraDB
- Pexels API

## Deployment
- Vercel
- Render

---

# 📂 Project Structure

```bash
TripGenius-AI/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   │
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── runtime.txt
│   └── .env
│
└── README.md
```

---

# ⚙️ Environment Variables

Create a `.env` file inside the backend folder.

```env
GEMINI_API_KEY=your_gemini_api_key

PEXELS_API_KEY=your_pexels_api_key

NEO4J_URI=your_neo4j_uri

NEO4J_USERNAME=your_neo4j_username

NEO4J_PASSWORD=your_neo4j_password
```

---

# 🔑 API Services Used

## Gemini AI

Used for:
- AI itinerary generation
- Smart travel recommendations
- Budget planning
- Hotel recommendations

---

## Pexels API

Used for:
- Dynamic destination images
- Day-wise travel visuals

---

## Neo4j AuraDB

Used for:
- Graph database storage
- Search history
- Trip relationships
- User travel graph visualization

---

# 🧠 Neo4j Graph Features

TripGenius AI stores:

- Destinations
- Interests
- Trip searches
- Day plans
- Budget details
- Food preferences
- Itineraries

Example relationships:

```text
(User)-[:SEARCHED]->(Destination)

(Destination)-[:HAS_INTEREST]->(Interest)

(Trip)-[:GENERATED_PLAN]->(Itinerary)
```

---

# ▶️ Run Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# ▶️ Run Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

---

# ☁️ Deployment

## Frontend Deployment
Deployed using:
- Vercel

## Backend Deployment
Deployed using:
- Render

---

# 🌟 Example Destinations Tested

- Japan 🇯🇵
- Switzerland 🇨🇭
- Sri Lanka 🇱🇰
- Dubai 🇦🇪
- Thailand 🇹🇭
- Australia 🇦🇺
- India 🇮🇳

---

# 🔮 Future Enhancements

- User authentication
- Real-time weather integration
- Flight & hotel APIs
- Interactive maps
- PDF itinerary export
- Multi-user saved trips
- AI chatbot travel assistant

---

# 👨‍💻 Developer

## Sadvik Kondadi

GitHub:
https://github.com/SadvikKondadi

---

# ⭐ If you like this project

Give it a ⭐ on GitHub!

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import os
import hashlib
from datetime import datetime

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


class AuthRequest(BaseModel):
    email: str
    password: str


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.post("/register")
def register_user(data: AuthRequest):
    email = data.email.strip().lower()
    password = hash_password(data.password)

    with driver.session() as session:
        existing = session.run(
            "MATCH (u:User {email: $email}) RETURN u",
            email=email,
        ).single()

        if existing:
            return {
                "success": False,
                "message": "User already exists",
            }

        session.run(
            """
            CREATE (u:User {
                email: $email,
                password: $password,
                created_at: $created_at
            })
            """,
            email=email,
            password=password,
            created_at=datetime.now().isoformat(),
        )

    return {
        "success": True,
        "message": "Registration successful",
        "email": email,
    }


@app.post("/login")
def login_user(data: AuthRequest):
    email = data.email.strip().lower()
    password = hash_password(data.password)

    with driver.session() as session:
        user = session.run(
            """
            MATCH (u:User {email: $email, password: $password})
            RETURN u
            """,
            email=email,
            password=password,
        ).single()

        if not user:
            return {
                "success": False,
                "message": "Invalid email or password",
            }

    return {
        "success": True,
        "message": "Login successful",
        "email": email,
    }


@app.post("/reset-password")
def reset_password(data: AuthRequest):
    email = data.email.strip().lower()
    new_password = hash_password(data.password)

    with driver.session() as session:
        existing = session.run(
            """
            MATCH (u:User {email: $email})
            RETURN u
            """,
            email=email,
        ).single()

        if not existing:
            return {
                "success": False,
                "message": "Email not registered",
            }

        session.run(
            """
            MATCH (u:User {email: $email})
            SET u.password = $password
            """,
            email=email,
            password=new_password,
        )

    return {
        "success": True,
        "message": "Password reset successful",
    }


def search_pexels_image(query):
    headers = {
        "Authorization": PEXELS_API_KEY,
    }

    try:
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params={
                "query": query,
                "per_page": 1,
                "orientation": "landscape",
            },
            timeout=10,
        )

        data = response.json()

        if data.get("photos"):
            return data["photos"][0]["src"]["large"]

    except Exception as e:
        print("Pexels Error:", e)

    return "https://images.pexels.com/photos/346885/pexels-photo-346885.jpeg"


def build_fallback_trip(destination, days, budget, food, interests):
    total_days = int(days) if str(days).isdigit() else 3
    interest_list = [i.strip() for i in interests.split(",") if i.strip()]

    day_cards = []

    for i in range(1, total_days + 1):
        interest = (
            interest_list[(i - 1) % len(interest_list)]
            if interest_list
            else "local attractions"
        )

        day_cards.append(
            {
                "day": f"Day {i}",
                "title": f"{destination} {interest.title()}",
                "summary": f"Explore {interest} in {destination}.",
                "route": f"Hotel → {interest.title()} → Food Area → Evening Spot",
                "image_query": f"{destination} {interest} travel",
            }
        )

    itinerary = f"""
# {total_days}-Day {destination} Travel Plan

## Trip Overview

- **Destination:** {destination}
- **Total Days:** {days}
- **Estimated Budget:** {budget}
- **Food Preference:** {food}
- **Interests:** {interests}

## Recommended Hotels

- Choose a hotel near the main tourist area.
- Stay close to public transport for easier travel.
- Pick an area near restaurants, markets, and attractions.

## Budget Breakdown

- **Hotels:** Around 40% of the budget
- **Food:** Around 20% of the budget
- **Transport:** Around 15% of the budget
- **Attractions:** Around 15% of the budget
- **Shopping/Miscellaneous:** Around 10% of the budget

## Transportation Guide

- Use local public transport when available.
- Keep nearby attractions grouped together.
- Use taxis or ride-share apps for late-night travel.

## Food Recommendations

- Try local food in **{destination}**.
- Include your food preference: **{food}**.
- Choose restaurants close to tourist areas and local markets.

## Day-wise Itinerary
"""

    for card in day_cards:
        itinerary += f"""

### {card["day"]}: {card["title"]}

- **Morning:** Start from your hotel and visit a popular place related to **{card["title"]}**.
- **Afternoon:** Explore nearby attractions, markets, scenic areas, or cultural spots.
- **Evening:** Try local food and enjoy an evening walk.
- **Estimated Daily Cost:** Depends on hotel, attraction tickets, food, and transport.
"""

    itinerary += """

## Hidden Gems

- Explore local neighborhoods.
- Visit smaller markets and viewpoints.
- Try authentic local food spots.

## Travel Tips

- Keep your documents and wallet safe.
- Book popular attractions early.
- Keep extra money for transport and emergencies.
- Avoid rushing too many places in one day.

## Final Estimated Total Cost

- Final cost depends on hotel category, transport choices, food, and attraction tickets.
"""

    return itinerary, day_cards


def create_day_cards(destination, days, interests):
    total_days = int(days) if str(days).isdigit() else 3
    interest_list = [i.strip() for i in interests.split(",") if i.strip()]

    day_cards = []

    for i in range(1, total_days + 1):
        interest = (
            interest_list[(i - 1) % len(interest_list)]
            if interest_list
            else "travel"
        )

        day_cards.append(
            {
                "day": f"Day {i}",
                "title": f"{destination} {interest.title()}",
                "summary": f"Explore {interest} in {destination} with sightseeing, food, and local experiences.",
                "route": f"Hotel → {interest.title()} → Food Area → Evening Spot",
                "image_query": f"{destination} {interest} travel",
            }
        )

    return day_cards


def save_trip_to_neo4j(
    destination,
    days,
    budget,
    food,
    interests,
    itinerary,
    day_cards,
    user_email=None,
):
    search_id = f"{destination}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    created_at = datetime.now().isoformat()
    interest_list = [i.strip() for i in interests.split(",") if i.strip()]

    with driver.session() as session:
        session.run(
            """
            MERGE (city:City {name: $destination})

            CREATE (search:TripSearch {
                id: $search_id,
                destination: $destination,
                days: $days,
                budget: $budget,
                food: $food,
                interests: $interests,
                created_at: $created_at,
                user_email: $user_email
            })

            CREATE (plan:Itinerary {
                text: $itinerary,
                created_at: $created_at
            })

            MERGE (budgetNode:Budget {amount: $budget})
            MERGE (foodNode:FoodPreference {name: $food})
            MERGE (durationNode:TripDuration {days: $days})

            MERGE (search)-[:REQUESTED_TRIP]->(city)
            MERGE (search)-[:GENERATED_PLAN]->(plan)
            MERGE (search)-[:HAS_BUDGET]->(budgetNode)
            MERGE (search)-[:HAS_FOOD_PREFERENCE]->(foodNode)
            MERGE (search)-[:HAS_DURATION]->(durationNode)
            MERGE (plan)-[:FOR_CITY]->(city)
            """,
            search_id=search_id,
            destination=destination,
            days=str(days),
            budget=budget,
            food=food,
            interests=interests,
            itinerary=itinerary,
            created_at=created_at,
            user_email=user_email,
        )

        if user_email:
            session.run(
                """
                MATCH (search:TripSearch {id: $search_id})
                MERGE (user:User {email: $user_email})
                MERGE (user)-[:SEARCHED]->(search)
                """,
                search_id=search_id,
                user_email=user_email,
            )

        for interest in interest_list:
            session.run(
                """
                MATCH (city:City {name: $destination})
                MERGE (interest:Interest {name: $interest})
                MERGE (city)-[:HAS_INTEREST]->(interest)
                """,
                destination=destination,
                interest=interest,
            )

        for card in day_cards:
            session.run(
                """
                MATCH (city:City {name: $destination})
                MERGE (day:TripDay {
                    destination: $destination,
                    day: $day
                })
                SET day.title = $title,
                    day.summary = $summary,
                    day.route = $route,
                    day.image = $image,
                    day.image_query = $image_query

                MERGE (city)-[:HAS_DAY_PLAN]->(day)
                """,
                destination=destination,
                day=card.get("day"),
                title=card.get("title"),
                summary=card.get("summary"),
                route=card.get("route"),
                image=card.get("image"),
                image_query=card.get("image_query"),
            )


@app.get("/")
def home():
    return {
        "message": "AI GraphRAG Travel Planner Backend Running",
    }


@app.post("/plan-trip")
def plan_trip(data: dict):
    destination = data.get("destination", "").strip()
    days = data.get("days", "3")
    budget = data.get("budget", "")
    food = data.get("food", "")
    interests = data.get("interests", "")
    user_email = data.get("user_email", "")

    cypher = """
    MATCH (n)-[:LOCATED_IN]->(c:City)
    WHERE toLower(c.name) CONTAINS toLower($destination)
    RETURN
        labels(n) AS type,
        n.name AS name,
        n.type AS category,
        n.cost AS cost,
        n.cuisine AS cuisine,
        n.price AS price
    LIMIT 30
    """

    with driver.session() as session:
        result = session.run(cypher, destination=destination)
        places = [record.data() for record in result]

    prompt = f"""
You are a premium AI travel planner.

Create a detailed, destination-specific travel itinerary in clean Markdown.

User Details:
- Destination: {destination}
- Days: {days}
- Budget: {budget}
- Food Preference: {food}
- Interests: {interests}

Neo4j Graph Data:
{places}

Very Important Rules:
- Return ONLY Markdown.
- Do NOT return JSON.
- Do NOT use code blocks.
- Do NOT use generic phrases.
- Mention real hotels, real areas, real attractions, real transport options, and realistic budget estimates.
- Make the itinerary specific to {destination}.
- Match the itinerary with the user's interests.
- Include hotel/accommodation recommendations.
- Include budget breakdown.
- Include transportation guide.
- Include food recommendations.
- Include day-wise itinerary.
- Include hidden gems.
- Include travel tips.
- Include final estimated total cost.

Use this exact structure:

# {days}-Day {destination} Travel Plan

## Trip Overview
- Destination:
- Total Days:
- Estimated Budget:
- Best Time to Visit:
- Travel Style:

## Recommended Hotels
Give 3 real hotel recommendations with:
- hotel name
- area
- approximate cost
- why recommended

## Budget Breakdown
Use bullets:
- Hotels:
- Food:
- Transport:
- Attractions:
- Shopping:
- Miscellaneous:

## Transportation Guide
Include:
- airport transport
- local transport
- train/metro/taxi recommendations
- daily travel tips

## Food Recommendations
Include:
- famous local dishes
- recommended food streets/areas/restaurants
- Indian food availability if requested

## Day-wise Itinerary
For every day include:
- Morning
- Afternoon
- Evening
- Nearby attractions
- Food suggestions
- Estimated daily cost

## Hidden Gems
Mention less touristy places.

## Travel Tips
Include safety, money saving, local etiquette, and useful apps.

## Final Estimated Total Cost
Give approximate total trip spending.
"""

    try:
        print("Calling Gemini...")
        response = model.generate_content(prompt)
        print("Gemini response received")

        itinerary = response.text

        if not itinerary or len(itinerary.strip()) < 100:
            raise Exception("Gemini returned empty or too short response")

        day_cards = create_day_cards(
            destination,
            days,
            interests,
        )

    except Exception as e:
        print("Gemini Error:", e)

        itinerary, day_cards = build_fallback_trip(
            destination,
            days,
            budget,
            food,
            interests,
        )

    for card in day_cards:
        image_query = card.get("image_query", f"{destination} travel")
        card["image"] = search_pexels_image(image_query)

    hero_image = (
        day_cards[0]["image"]
        if day_cards
        else search_pexels_image(f"{destination} travel")
    )

    gallery = [card["image"] for card in day_cards[:3]]
    day_images = [card["image"] for card in day_cards]

    images = {
        "hero": hero_image,
        "gallery": gallery,
        "day_images": day_images,
    }

    save_trip_to_neo4j(
        destination=destination,
        days=days,
        budget=budget,
        food=food,
        interests=interests,
        itinerary=itinerary,
        day_cards=day_cards,
        user_email=user_email,
    )

    return {
        "success": True,
        "destination": destination,
        "days": days,
        "budget": budget,
        "food": food,
        "interests": interests,
        "places_used": places,
        "images": images,
        "day_cards": day_cards,
        "itinerary": itinerary,
    }


@app.get("/graph-data")
def graph_data():
    query = """
    MATCH (a)-[r]->(b)
    RETURN
        a.name AS source,
        type(r) AS relationship,
        b.name AS target
    LIMIT 300
    """

    with driver.session() as session:
        result = session.run(query)
        graph = [record.data() for record in result]

    return {
        "graph": graph,
    }


@app.get("/search-history")
def search_history():
    query = """
    MATCH (s:TripSearch)-[:REQUESTED_TRIP]->(c:City)
    RETURN
        s.id AS id,
        c.name AS destination,
        s.days AS days,
        s.budget AS budget,
        s.food AS food,
        s.interests AS interests,
        s.user_email AS user_email,
        s.created_at AS created_at
    ORDER BY s.created_at DESC
    LIMIT 50
    """

    with driver.session() as session:
        result = session.run(query)
        searches = [record.data() for record in result]

    return {
        "searches": searches,
    }


@app.get("/health")
def health():
    return {
        "status": "running",
        "ai": "Gemini",
        "database": "Neo4j AuraDB",
        "backend": "FastAPI",
    }
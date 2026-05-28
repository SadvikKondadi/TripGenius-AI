from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import os
import json
import re
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


def search_pexels_image(query):
    headers = {"Authorization": PEXELS_API_KEY}

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


def clean_json_response(text):
    text = text.strip()
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()


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
                "title": f"{destination} {interest.title()} Experience",
                "summary": f"Explore {interest} in {destination} with food, sightseeing, and local culture.",
                "route": f"Hotel → {interest.title()} Spot → Local Food → Evening Walk",
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

- **Budget Hotel:** Stay near the main tourist area for easy transport.
- **Mid-range Hotel:** Choose a hotel close to metro, train, or central attractions.
- **Comfort Stay:** Pick a hotel near food streets and major sightseeing points.

## Budget Breakdown

- **Hotels:** 40% of total budget
- **Food:** 20% of total budget
- **Transport:** 15% of total budget
- **Attractions:** 15% of total budget
- **Shopping/Miscellaneous:** 10% of total budget

## Transportation Guide

- Use local metro, trains, taxis, or ride-share apps depending on the city.
- Group nearby places together to save time and money.
- Keep evenings close to your hotel area.

## Food Recommendations

- Try local food in **{destination}**.
- Include your preference: **{food}**.
- Choose restaurants near tourist areas and local markets.

## Day-wise Itinerary
"""

    for card in day_cards:
        itinerary += f"""

### {card["day"]}: {card["title"]}

- **Morning:** Start from your hotel and visit a famous place related to this day.
- **Afternoon:** Explore nearby attractions, markets, or scenic areas.
- **Evening:** Try local food and enjoy an evening walk.
- **Estimated Daily Cost:** Depends on hotel, tickets, food, and transport choices.
"""

    itinerary += """

## Hidden Gems

- Explore local neighborhoods.
- Visit smaller markets and scenic viewpoints.
- Try authentic local food spots.

## Travel Tips

- Keep your documents and wallet safe.
- Book popular attractions early.
- Keep extra money for transport and emergencies.
- Avoid rushing too many places in one day.

## Final Estimated Total Cost

- Your final cost depends on hotel category, transport choices, food, and attraction tickets.
"""

    return itinerary, day_cards


def save_trip_to_neo4j(destination, days, budget, food, interests, itinerary, day_cards):
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
                created_at: $created_at
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
    return {"message": "AI GraphRAG Travel Planner Backend Running"}


@app.post("/plan-trip")
def plan_trip(data: dict):
    destination = data.get("destination", "").strip()
    days = data.get("days", "3")
    budget = data.get("budget", "")
    food = data.get("food", "")
    interests = data.get("interests", "")

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

Generate a destination-specific travel plan for ANY location in the world.

User details:
Destination: {destination}
Days: {days}
Budget: {budget}
Food Preference: {food}
Interests: {interests}

Neo4j graph data:
{places}

Return ONLY valid JSON. No markdown outside JSON. No code fences.

JSON format:
{{
  "itinerary_markdown": "clean markdown itinerary here",
  "day_cards": [
    {{
      "day": "Day 1",
      "title": "specific day title",
      "summary": "short day summary",
      "route": "Hotel → Specific Place → Food Area → Evening Spot",
      "image_query": "specific Pexels image search query"
    }}
  ]
}}

Rules:
- The itinerary must be specific to {destination}.
- Day cards must match the itinerary exactly.
- Image queries must be specific places or experiences from {destination}.
- Do not use generic words only.
- Do not suggest wrong activities for the destination.
- Create exactly {days} day cards if possible.
- Use Markdown inside itinerary_markdown.
- Do not create markdown tables.
- Include hotel/accommodation recommendations.
- Include budget breakdown.
- Include transportation guide.
- Include local food recommendations.
- Include estimated total cost.
- Include hidden gems and travel tips.

The itinerary_markdown must use this exact structure:

# {days}-Day {destination} Travel Plan

## Trip Overview
- Destination:
- Total Days:
- Estimated Budget:
- Best Time to Visit:
- Travel Style:

## Recommended Hotels
Give 3 hotel recommendations:
- hotel name
- area
- approximate cost
- why recommended

## Budget Breakdown
Use bullets only:
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
- metro/train/taxi recommendations
- daily travel tips

## Food Recommendations
Include:
- famous local dishes
- recommended restaurants or food areas
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

Destination-specific examples:
- India: Taj Mahal, India Gate, Jaipur, Kerala, Goa, Varanasi depending on interests.
- Japan: Tokyo, Kyoto, Osaka, Mount Fuji, Hakone, Shibuya, Akihabara, bullet trains.
- Switzerland: Alps, Interlaken, Lucerne, Zermatt, lakes, scenic trains, snow, hiking.
- Sri Lanka: Sigiriya, Galle, Ella, Kandy, Mirissa, Yala, tea plantations.
- Dubai: Burj Khalifa, Desert Safari, Dubai Marina, Palm Jumeirah, Dubai Mall.
- Thailand: Bangkok, Phuket, Krabi, Chiang Mai, temples, beaches, islands, night markets.
- Australia: Sydney Opera House, Great Barrier Reef, Melbourne, Gold Coast, wildlife, beaches.
"""

    try:
        print("Calling Gemini...")
        response = model.generate_content(prompt)
        print("Gemini response received")

        parsed = json.loads(clean_json_response(response.text))

        itinerary = parsed.get("itinerary_markdown", "")
        day_cards = parsed.get("day_cards", [])

        if not itinerary or not day_cards:
            itinerary, day_cards = build_fallback_trip(
                destination,
                days,
                budget,
                food,
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

    return {"graph": graph}


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
        s.created_at AS created_at
    ORDER BY s.created_at DESC
    LIMIT 50
    """

    with driver.session() as session:
        result = session.run(query)
        searches = [record.data() for record in result]

    return {"searches": searches}


@app.get("/health")
def health():
    return {
        "status": "running",
        "ai": "Gemini",
        "database": "Neo4j AuraDB",
        "backend": "FastAPI",
    }
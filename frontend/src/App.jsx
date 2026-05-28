import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import {
  Plane,
  MapPin,
  Hotel,
  Utensils,
  Camera,
  Save,
  Sparkles,
  Compass,
} from "lucide-react";
import "./App.css";

const BASE_URL = "https://tripgenius-ai-backend.onrender.com";
const API_URL = `${BASE_URL}/plan-trip`;

const fallbackImages = {
  hero: "https://images.pexels.com/photos/346885/pexels-photo-346885.jpeg",
  gallery: [
    "https://images.pexels.com/photos/346885/pexels-photo-346885.jpeg",
    "https://images.pexels.com/photos/21014/pexels-photo.jpg",
    "https://images.pexels.com/photos/672358/pexels-photo-672358.jpeg",
  ],
  day_images: [
    "https://images.pexels.com/photos/346885/pexels-photo-346885.jpeg",
    "https://images.pexels.com/photos/21014/pexels-photo.jpg",
    "https://images.pexels.com/photos/672358/pexels-photo-672358.jpeg",
    "https://images.pexels.com/photos/338515/pexels-photo-338515.jpeg",
  ],
};

function Navbar({ user, setUser }) {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("travel_user");
    setUser(null);
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="brand">
        <Plane size={28} />
        <span>TripGenius AI</span>
      </div>

      {user && (
        <div className="nav-links">
          <Link to="/">Dashboard</Link>
          <Link to="/planner">Planner</Link>
          <Link to="/saved">Saved Trips</Link>
          <Link to="/about">About</Link>
          <button onClick={logout}>Logout</button>
        </div>
      )}
    </nav>
  );
}

function Login({ setUser }) {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const login = async () => {
    if (!email || !password) {
      return alert("Enter email and password");
    }

    try {
      const res = await axios.post(`${BASE_URL}/login`, {
        email,
        password,
      });

      if (!res.data.success) {
        return alert(res.data.message);
      }

      localStorage.setItem("travel_user", res.data.email);
      setUser(res.data.email);
      navigate("/");
    } catch (error) {
      alert("Login failed. Backend not reachable.");
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card glass">
        <h1>Welcome Back ✈️</h1>
        <p>Your AI travel assistant is ready.</p>

        <input
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          placeholder="Password"
          type="password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={login}>Login</button>

        <p>
          New user? <Link to="/register">Create account</Link>
        </p>
      </div>
    </div>
  );
}

function Register({ setUser }) {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const register = async () => {
    if (!email || !password) {
      return alert("Enter email and password");
    }

    try {
      const res = await axios.post(`${BASE_URL}/register`, {
        email,
        password,
      });

      if (!res.data.success) {
        return alert(res.data.message);
      }

      localStorage.setItem("travel_user", res.data.email);
      setUser(res.data.email);
      navigate("/");
    } catch (error) {
      alert("Registration failed. Backend not reachable.");
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card glass">
        <h1>Create Account 🌍</h1>
        <p>Start planning beautiful AI-powered trips.</p>

        <input placeholder="Full Name" />

        <input
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          placeholder="Password"
          type="password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={register}>Register</button>

        <p>
          Already have account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}

function Dashboard({ user }) {
  return (
    <div className="page">
      <section className="hero">
        <div>
          <p className="badge">AI + Neo4j + Gemini + Pexels</p>
          <h1>Plan trips that feel personal, smart, and beautiful.</h1>
          <p>
            Generate destination-specific itineraries with real travel images,
            route cards, food suggestions, and saved trip history.
          </p>

          <Link className="primary-btn" to="/planner">
            Start Planning
          </Link>
        </div>
      </section>

      <div className="features">
        <div className="feature-card">
          <MapPin />
          <h3>Smart Routes</h3>
          <p>Places arranged like a real trip flow.</p>
        </div>

        <div className="feature-card">
          <Sparkles />
          <h3>AI Itinerary</h3>
          <p>Gemini creates personalized plans.</p>
        </div>

        <div className="feature-card">
          <Compass />
          <h3>GraphRAG</h3>
          <p>Neo4j stores searches, interests, images, and trip plans.</p>
        </div>

        <div className="feature-card">
          <Save />
          <h3>Saved Trips</h3>
          <p>Saved trips are private for each login.</p>
        </div>
      </div>

      <p className="welcome">Logged in as: {user}</p>
    </div>
  );
}

function Planner() {
  const [form, setForm] = useState({
    destination: "Australia",
    days: "5",
    budget: "$1800",
    food: "Australian and Indian food",
    interests:
      "beaches, wildlife, road trips, surfing, opera house, reefs, nightlife",
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [images, setImages] = useState(fallbackImages);
  const [dayCards, setDayCards] = useState([]);

  const jokes = [
    "My suitcase and I have a lot in common. We both get carried away.",
    "Vacation calories do not count. That is officially my travel policy.",
    "I followed my heart and it led me to the airport.",
  ];

  const quote =
    "Travel is not just about the destination, it is about the memories you create on the way.";

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const generateTrip = async () => {
    setLoading(true);
    setResult("");
    setImages(fallbackImages);
    setDayCards([]);

    try {
      const currentUser = localStorage.getItem("travel_user");

      const res = await axios.post(API_URL, {
        ...form,
        user_email: currentUser,
      });

      setResult(res.data.itinerary || "No itinerary generated.");
      setImages(res.data.images || fallbackImages);
      setDayCards(res.data.day_cards || []);
    } catch (err) {
      console.log(err);
      setResult("Error generating trip. Make sure backend is running.");
    }

    setLoading(false);
  };

  const saveTrip = () => {
    const currentUser = localStorage.getItem("travel_user");

    const trips =
      JSON.parse(localStorage.getItem(`saved_trips_${currentUser}`)) || [];

    trips.push({
      ...form,
      itinerary: result,
      images,
      dayCards,
      date: new Date().toLocaleString(),
    });

    localStorage.setItem(`saved_trips_${currentUser}`, JSON.stringify(trips));

    alert("Trip saved successfully!");
  };

  return (
    <div className="planner-page">
      <section className="planner-hero">
        <div>
          <p className="badge">Interactive AI Travel Builder</p>
          <h1>Design your dream trip in seconds</h1>
          <p>
            Enter any destination in the world. The AI creates matching
            itinerary, route cards, and location-based images together.
          </p>
        </div>
      </section>

      <div className="image-strip">
        {images.gallery.map((img, index) => (
          <img
            src={img}
            alt={`${form.destination} gallery ${index + 1}`}
            key={index}
          />
        ))}
      </div>

      <div className="planner-layout">
        <div className="form-card glass">
          <h2>Trip Details</h2>

          <label>Destination</label>
          <input
            name="destination"
            value={form.destination}
            onChange={handleChange}
          />

          <label>Days</label>
          <input name="days" value={form.days} onChange={handleChange} />

          <label>Budget</label>
          <input name="budget" value={form.budget} onChange={handleChange} />

          <label>Food Preference</label>
          <input name="food" value={form.food} onChange={handleChange} />

          <label>Interests</label>
          <input
            name="interests"
            value={form.interests}
            onChange={handleChange}
          />

          <button onClick={generateTrip}>
            {loading ? "Creating Magic..." : "Generate Trip"}
          </button>

          <div className="quote-box">
            <Sparkles size={18} />
            <p>{quote}</p>
          </div>
        </div>

        <div className="result-section">
          <div className="destination-preview">
            <img src={images.hero} alt={form.destination} />

            <div className="destination-overlay">
              <h2>{form.destination} Itinerary</h2>
              <p>
                {form.days} days • {form.budget} budget • {form.food}
              </p>
            </div>
          </div>

          <div className="route-card glass">
            <h2>Suggested Route Flow</h2>

            <div className="route-line">
              <div>
                <Hotel />
                Hotel
              </div>

              <span></span>

              <div>
                <Camera />
                {dayCards[0]?.title || "Attraction"}
              </div>

              <span></span>

              <div>
                <Utensils />
                {form.food}
              </div>

              <span></span>

              <div>
                <MapPin />
                {dayCards[dayCards.length - 1]?.title || "Evening Spot"}
              </div>
            </div>
          </div>

          {dayCards.length > 0 && (
            <div className="interactive-days">
              {dayCards.map((day, index) => (
                <div className="day-card" key={index}>
                  <img src={day.image} alt={day.title} />

                  <div>
                    <h3>
                      {day.day}: {day.title}
                    </h3>
                    <p>{day.summary}</p>
                    <span>{day.route}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="joke-card">
            <h3>Travel Joke 😄</h3>
            <p>{jokes[Math.floor(Math.random() * jokes.length)]}</p>
          </div>

          <div className="output-card glass">
            <h2>Detailed AI Travel Guide</h2>

            {loading && (
              <div className="loader">
                <div className="spinner"></div>
                <p>Building your matching itinerary and day cards...</p>
              </div>
            )}

            {!loading && !result && (
              <div className="empty-state">
                <Plane size={45} />
                <p>Your interactive travel plan will appear here.</p>
              </div>
            )}

            {result && (
              <>
                <div className="smart-summary">
                  <div>
                    <h3>🌍 Destination</h3>
                    <p>{form.destination}</p>
                  </div>

                  <div>
                    <h3>📅 Duration</h3>
                    <p>{form.days} Days</p>
                  </div>

                  <div>
                    <h3>💰 Budget</h3>
                    <p>{form.budget}</p>
                  </div>

                  <div>
                    <h3>🍽️ Food</h3>
                    <p>{form.food}</p>
                  </div>
                </div>

                <div className="ai-card">
                  <h3>✨ AI Recommendation</h3>

                  <div className="itinerary-text">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {result}
                    </ReactMarkdown>
                  </div>
                </div>

                <button className="save-btn" onClick={saveTrip}>
                  Save This Beautiful Trip
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SavedTrips() {
  const currentUser = localStorage.getItem("travel_user");

  const [trips, setTrips] = useState(
    JSON.parse(localStorage.getItem(`saved_trips_${currentUser}`)) || []
  );

  const deleteTrip = (index) => {
    const updated = trips.filter((_, i) => i !== index);

    setTrips(updated);

    localStorage.setItem(`saved_trips_${currentUser}`, JSON.stringify(updated));
  };

  return (
    <div className="page">
      <h1 className="page-title">Saved Trips</h1>

      {trips.length === 0 ? (
        <p className="empty">No saved trips yet.</p>
      ) : (
        trips.map((trip, index) => (
          <div className="saved-card glass" key={index}>
            <h2>{trip.destination}</h2>

            <p>
              {trip.days} days | {trip.budget} | {trip.food}
            </p>

            {trip.dayCards && trip.dayCards.length > 0 && (
              <div className="interactive-days">
                {trip.dayCards.map((day, dayIndex) => (
                  <div className="day-card" key={dayIndex}>
                    <img src={day.image} alt={day.title} />

                    <div>
                      <h3>
                        {day.day}: {day.title}
                      </h3>
                      <p>{day.summary}</p>
                      <span>{day.route}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="itinerary-text">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {trip.itinerary}
              </ReactMarkdown>
            </div>

            <button onClick={() => deleteTrip(index)}>Delete</button>
          </div>
        ))
      )}
    </div>
  );
}

function About() {
  return (
    <div className="page about glass">
      <h1>About This Project</h1>

      <p>
        TripGenius AI is an end-to-end AI GraphRAG travel planner built using
        React, FastAPI, Neo4j AuraDB, Gemini AI, Pexels API, and Cypher queries.
      </p>

      <div className="tech-stack">
        <span>React</span>
        <span>FastAPI</span>
        <span>Neo4j</span>
        <span>Gemini AI</span>
        <span>Pexels API</span>
        <span>GraphRAG</span>
      </div>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(localStorage.getItem("travel_user"));

  return (
    <>
      <Navbar user={user} setUser={setUser} />

      <Routes>
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/register" element={<Register setUser={setUser} />} />

        <Route
          path="/"
          element={user ? <Dashboard user={user} /> : <Login setUser={setUser} />}
        />

        <Route
          path="/planner"
          element={user ? <Planner /> : <Login setUser={setUser} />}
        />

        <Route
          path="/saved"
          element={user ? <SavedTrips /> : <Login setUser={setUser} />}
        />

        <Route
          path="/about"
          element={user ? <About /> : <Login setUser={setUser} />}
        />
      </Routes>
    </>
  );
}

export default App;
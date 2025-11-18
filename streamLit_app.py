import streamlit as st
from datetime import datetime, timedelta
import time
import random # Import for random cost generation

# 1. Page Configuration (Must be first)
st.set_page_config(
    page_title="AI Travel Planner Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for the "Pro" Look (Dark theme, Orange accents)
st.markdown("""
    <style>
    /* Main Background stuff */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar styling and ensuring white text for labels/titles */
    [data-testid="stSidebar"] {
        background-color: #262730;
    }
    
    /* Ensuring all input labels and titles in the sidebar are white */
    .stTextInput label, .stDateInput label, .stNumberInput label, .stSelectbox label, .stMultiSelect label, 
    [data-testid="stSidebar"] .stTitle, [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
    }
    
    /* Custom Button Style (Orange Gradient) */
    div.stButton > button {
        background: linear-gradient(45deg, #FF4B4B, #FF8F00);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
    }
    /* FIX: Remove white hover effect and customize hover appearance */
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        /* Slight color change on hover to hide the default white shadow */
        background: linear-gradient(45deg, #D44040, #D47A00) !important; 
        color: white !important;
        border-color: transparent !important;
    }
    /* FIX: Remove white box-shadow on focus (after click) */
    div.stButton > button:focus:not(:active) {
        box-shadow: 0 0 0 0.2rem rgba(255, 75, 75, 0.4) !important; 
        outline: none !important;
    }

    /* Itinerary Card Styling */
    .day-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .time-slot {
        color: #FF8F00;
        font-weight: bold;
        font-size: 1.1em;
    }
    .activity-title {
        color: #FFFFFF;
        font-size: 1.2em;
        font-weight: 600;
    }
    .cost-tag {
        background-color: #333;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.8em;
        color: #4CAF50;
        margin-left: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Helper Function: Mock Data Generator (UPDATED FOR DYNAMIC COSTS)
def generate_mock_itinerary(dest, days, budget_level, currency, interests):
    # Determine the symbol for display
    budget_symbol = "₹" if currency == "Indian Rupees (₹)" else "$"

    # Define cost ranges based on budget level for different activity types
    cost_ranges = {
        "Budget": {
            "meal": (10, 30), "attraction": (20, 50), "misc": (5, 20)
        },
        "Moderate": {
            "meal": (30, 70), "attraction": (50, 100), "misc": (20, 50)
        },
        "Luxury": {
            "meal": (70, 150), "attraction": (100, 250), "misc": (50, 100)
        }
    }
    
    # Get the specific cost range for the selected budget_level
    current_cost_range = cost_ranges.get(budget_level, cost_ranges["Moderate"]) # Default to Moderate if not found

    itinerary = []
    current_date = datetime.now()
    
    for i in range(1, days + 1):
        # Generate random costs within the defined ranges
        breakfast_cost = random.randint(*current_cost_range["meal"])
        museum_cost = random.randint(*current_cost_range["attraction"])
        street_food_cost = random.randint(*current_cost_range["misc"])
        dinner_cost = random.randint(*current_cost_range["meal"])

        # Add a slight boost if 'Shopping' is an interest for mock purposes
        if "Shopping" in interests and budget_level == "Luxury":
            museum_cost += random.randint(20, 50) # Mock increase for luxury shopping-focused trips

        day_plan = {
            "day": i,
            "date": (current_date + timedelta(days=i)).strftime("%B %d"),
            "theme": f"Exploring {interests[0] if interests else 'Culture'} & Local Gems",
            "activities": [
                {"time": "09:00 AM", "activity": f"Breakfast at {dest}'s famous cafe", "cost": f"{budget_symbol} {breakfast_cost}"},
                {"time": "11:00 AM", "activity": f"Visit the Top Museum in {dest}", "cost": f"{budget_symbol} {museum_cost}"},
                {"time": "01:30 PM", "activity": "Local Street Food Tour", "cost": f"{budget_symbol} {street_food_cost}"},
                {"time": "04:00 PM", "activity": "Relaxing walk through the city park", "cost": "Free"},
                {"time": "07:30 PM", "activity": "Dinner with a View", "cost": f"{budget_symbol} {dinner_cost}"},
            ]
        }
        itinerary.append(day_plan)
    return itinerary

# 4. Data Converter for Text File (Download)
def convert_itinerary_to_text_content(itinerary_data, destination):
    """Converts the itinerary data into a readable text format."""
    text_output = f"TRAVEL ITINERARY: {destination.upper()}\n"
    text_output += f"Generated On: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text_output += "--------------------------------------------------------\n"
    
    for day in itinerary_data:
        text_output += f"\nDAY {day['day']}: {day['theme']} ({day['date']})\n"
        text_output += "--------------------------------------------------------\n"
        for act in day['activities']:
            text_output += f"{act['time']} | {act['cost']:<6} | {act['activity']}\n"
        
    return text_output.encode('utf-8')


# 5. Sidebar - User Inputs
with st.sidebar:
    st.title("🌍 AI Travel Agent")
    st.markdown("---")
    
    # Inputs 
    destination = st.text_input("📍 Destination", placeholder="e.g., Paris, Tokyo, New York")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 Start Date")
    with col2:
        duration = st.number_input("🌙 Days", min_value=1, max_value=30, value=3)

    # CURRENCY SELECTION
    col3, col4 = st.columns(2)
    with col3:
        currency = st.selectbox("💲 Currency", ["US Dollars ($)", "Indian Rupees (₹)"])
    with col4:
        budget_level = st.selectbox("💰 Budget Level", ["Budget", "Moderate", "Luxury"])
        
    interests = st.multiselect(
        "❤️ Interests",
        ["History", "Art", "Food", "Nature", "Shopping", "Nightlife", "Adventure"],
        default=["Food", "Nature"]
    )
    
    st.markdown("---")

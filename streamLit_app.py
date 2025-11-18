import streamlit as st
from datetime import datetime, timedelta
import time
import random

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
    /* Flight Card Styling */
    .flight-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF8F00;
        margin-bottom: 25px;
    }
    .flight-time {
        font-weight: bold;
        color: #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Helper Function: Mock Data Generator (UPDATED TO INCLUDE FLIGHTS)
def generate_mock_itinerary(dest, start_date, duration, budget_level, currency, interests):
    budget_symbol = "₹" if currency == "Indian Rupees (₹)" else "$"
    
    # --- FLIGHT GENERATION LOGIC ---
    # Define base flight prices for mock purposes (e.g., in USD before conversion)
    base_flight_prices = {
        "Budget": (150, 400),
        "Moderate": (400, 800),
        "Luxury": (800, 1500)
    }
    
    # Mock conversion (very simple, non-accurate rate for demonstration)
    conversion_rate = 83 if budget_symbol == "₹" else 1 

    flight_range = base_flight_prices.get(budget_level, base_flight_prices["Moderate"])
    
    # Calculate flight price and round to the nearest 100 or 50 for Indian Rupees
    raw_flight_price = random.randint(*flight_range) * conversion_rate
    if budget_symbol == "₹":
        flight_price = round(raw_flight_price / 100) * 100
    else:
        flight_price = round(raw_flight_price / 5) * 5

    return_date = start_date + timedelta(days=duration)
    
    flight_details = {
        "outbound": {
            "date": start_date.strftime("%b %d, %Y"),
            "time": "08:30 AM",
            "from": "Origin City", # Using a generic origin for mock data
            "to": dest,
            "airline": "AirGo",
            "price": f"{budget_symbol} {flight_price}"
        },
        "return": {
            "date": return_date.strftime("%b %d, %Y"),
            "time": "06:00 PM",
            "from": dest,
            "to": "Origin City",
            "airline": "AirGo",
            "price": f"{budget_symbol} {flight_price}"
        }
    }
    
    # --- ITINERARY GENERATION LOGIC (Same as before, but using start_date correctly) ---
    cost_ranges = {
        "Budget": {"meal": (10, 30), "attraction": (20, 50), "misc": (5, 20)},
        "Moderate": {"meal": (30, 70), "attraction": (50, 100), "misc": (20, 50)},
        "Luxury": {"meal": (70, 150), "attraction": (100, 250), "misc": (50, 100)}
    }
    current_cost_range = cost_ranges.get(budget_level, cost_ranges["Moderate"])

    itinerary = []
    
    for i in range(duration):
        current_day_date = start_date + timedelta(days=i)
        
        # Costs for the daily activities
        breakfast_cost = random.randint(*current_cost_range["meal"])
        museum_cost = random.randint(*current_cost_range["attraction"])
        street_food_cost = random.randint(*current_cost_range["misc"])
        dinner_cost = random.randint(*current_cost_range["meal"])

        if "Shopping" in interests and budget_level == "Luxury":
            museum_cost += random.randint(20, 50) 

        day_plan = {
            "day": i + 1,
            "date": current_day_date.strftime("%B %d"),
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
        
    return itinerary, flight_details

# 4. Data Converter for Text File (Download)
def convert_itinerary_to_text_content(itinerary_data, destination, flight_data):
    """Converts the itinerary and flight data into a readable text format."""
    text_output = f"TRAVEL ITINERARY: {destination.upper()}\n"
    text_output += f"Generated On: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    # Add Flight Details to the text output
    text_output += "✈️ FLIGHT DETAILS ✈️\n"
    text_output += "--------------------------------------------------------\n"
    out = flight_data["outbound"]
    ret = flight_data["return"]
    
    text_output += f"OUTBOUND: {out['airline']} | {out['date']} @ {out['time']} | Price: {out['price']}\n"
    text_output += f"   -> Route: {out['from']} to {out['to']}\n"
    text_output += f"RETURN:   {ret['airline']} | {ret['date']} @ {ret['time']} | Price: {ret['price']}\n"
    text_output += f"   -> Route: {ret['from']} to {ret['to']}\n"
    text_output += "--------------------------------------------------------\n\n"
    
    # Add Daily Itinerary to the text output
    for day in itinerary_data:
        text_output += f"\n🗓️ DAY {day['day']}: {day['theme']} ({day['date']})\n"
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
        # NOTE: start_date is now used in flight calculation
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
    
    # The "Magic" Button
    generate_btn = st.button("✨ Generate Itinerary", key="generate_btn_sidebar")


# 6. Main Content Area
if not generate_btn and "itinerary" not in st.session_state:
    # Welcome Screen (State 0)
    st.header("✈️ Welcome to your Personal Travel Agent")
    st.markdown("""
    This AI Agent will curate a perfect trip for you based on your preferences.
    
    **How it works:**
    1. Enter your destination and dates in the sidebar on the left.
    2. Select your budget and specific interests.
    3. Click the **Generate Itinerary** button below the inputs!
    """)
    st.info("👈 Fill out the details in the sidebar and click the button to begin planning!")

else:
    # Loading State
    if generate_btn:
        with st.spinner(f"🤖 AI Agents are researching {destination}..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Generate Data - Receives both itinerary and flight details
            itinerary_data, flight_details = generate_mock_itinerary(
                destination, start_date, duration, budget_level, currency, interests
            )
            st.session_state.itinerary = itinerary_data
            st.session_state.flights = flight_details
            st.session_state.display_budget = f"{budget_level} ({currency})"
    
    # Result Display (State 1)
    if "itinerary" in st.session_state:
        data = st.session_state.itinerary
        flights = st.session_state.flights

        st.header(f"✈️ Your Trip to {destination}")
        st.markdown(f"**Duration:** {duration} Days | **Budget:** {st.session_state.display_budget}")
        st.markdown("---")

        
        # --- NEW: FLIGHT DETAILS DISPLAY ---
        st.subheader("🛫 Flight Details")
        
        col_out, col_ret = st.columns(2)
        
        # Outbound Flight
        with col_out:
            st.markdown(f"""
                <div class="flight-card">
                    **Outbound Flight**
                    <p class="flight-time">🕒 {flights['outbound']['time']} - {flights['outbound']['date']}</p>
                    <p>✈️ {flights['outbound']['airline']}</p>
                    <p>📍 {flights['outbound']['from']} → {flights['outbound']['to']}</p>
                    <p>💵 **Price:** {flights['outbound']['price']}</p>
                </div>
            """, unsafe_allow_html=True)
            
        # Return Flight
        with col_ret:
            st.markdown(f"""
                <div class="flight-card">
                    **Return Flight**
                    <p class="flight-time">🕒 {flights['return']['time']} - {flights['return']['date']}</p>
                    <p>✈️ {flights['return']['airline']}</p>
                    <p>📍 {flights['return']['from']} → {flights['return']['to']}</p>
                    <p>💵 **Price:** {flights['return']['price']}</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")

        # --- DAILY ITINERARY DISPLAY ---
        st.subheader("🗓️ Daily Itinerary")
        for day in data:
            with st.container():
                st.markdown(f"""
                <div class="day-card">
                    <h3 style="margin-top:0;">Day {day['day']}: {day['theme']}</h3>
                    <p style="color:#888; margin-bottom:15px;">{day['date']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                for act in day['activities']:
                    c1, c2, c3 = st.columns([2, 6, 2])
                    with c1:
                        st.markdown(f"<span class='time-slot'>{act['time']}</span>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<span class='activity-title'>{act['activity']}</span>", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"<span class='cost-tag'>{act['cost']}</span>", unsafe_allow_html=True)
                    st.divider()

        # 7. Download Option 
        text_download_data = convert_itinerary_to_text_content(data, destination, flights)

        st.markdown("### 📥 Download Itinerary")
        
        st.download_button(
            label="Download Itinerary as Text", 
            data=text_download_data, 
            file_name=f"{destination}_itinerary.txt", 
            mime="text/plain", 
            use_container_width=True
        )

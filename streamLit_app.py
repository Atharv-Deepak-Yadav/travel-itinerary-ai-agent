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
    
    /* GUARANTEED FIX: Ensuring all input labels and titles in the sidebar are white */
    /* This line targets the specific data-testid for all input labels */
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    
    /* Existing specific selectors (kept for robustness) */
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
    /* Total Cost Highlight */
    .total-cost-box {
        background-color: #333333;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 30px;
        border: 2px solid #FF8F00;
    }
    .total-cost-label {
        color: #FF4B4B;
        font-size: 1.2em;
        font-weight: bold;
    }
    .total-cost-value {
        color: #4CAF50;
        font-size: 2.2em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Helper Function: Mock Data Generator (UPDATED TO CALCULATE TOTAL COST)
def generate_mock_itinerary(dest, start_date, duration, budget_level, currency, interests):
    budget_symbol = "₹" if currency == "Indian Rupees (₹)" else "$"
    
    # --- FLIGHT GENERATION LOGIC ---
    base_flight_prices = {
        "Budget": (150, 400),
        "Moderate": (400, 800),
        "Luxury": (800, 1500)
    }
    
    # Mock conversion (1 USD = 83 INR for demonstration)
    conversion_rate = 83 if budget_symbol == "₹" else 1 

    flight_range = base_flight_prices.get(budget_level, base_flight_prices["Moderate"])
    
    # Base price calculation (using USD range, then multiplying by rate)
    raw_single_flight_price = random.randint(*flight_range) * conversion_rate
    
    # Rounding for clean currency display
    if budget_symbol == "₹":
        single_flight_price = round(raw_single_flight_price / 100) * 100
    else:
        single_flight_price = round(raw_single_flight_price / 5) * 5
        
    total_flight_cost = single_flight_price * 2 # Round trip

    return_date = start_date + timedelta(days=duration)
    
    flight_details = {
        "outbound": {
            "date": start_date.strftime("%b %d, %Y"),
            "time": "08:30 AM",
            "from": "Origin City",
            "to": dest,
            "airline": "AirGo",
            "price": single_flight_price, # Stored as raw number for total calculation
            "display_price": f"{budget_symbol} {single_flight_price}"
        },
        "return": {
            "date": return_date.strftime("%b %d, %Y"),
            "time": "06:00 PM",
            "from": dest,
            "to": "Origin City",
            "airline": "AirGo",
            "price": single_flight_price, # Stored as raw number for total calculation
            "display_price": f"{budget_symbol} {single_flight_price}"
        },
        "total_cost": total_flight_cost # Total flight cost
    }
    
    # --- ITINERARY GENERATION & DAILY COST CALCULATION ---
    cost_ranges = {
        "Budget": {"meal": (10, 30), "attraction": (20, 50), "misc": (5, 20)},
        "Moderate": {"meal": (30, 70), "attraction": (50, 100), "misc": (20, 50)},
        "Luxury": {"meal": (70, 150), "attraction": (100, 250), "misc": (50, 100)}
    }
    current_cost_range = cost_ranges.get(budget_level, cost_ranges["Moderate"])

    itinerary = []
    total_daily_cost = 0
    
    for i in range(duration):
        current_day_date = start_date + timedelta(days=i)
        
        # Costs for the daily activities (Base costs are in USD, then convert)
        breakfast_cost = random.randint(*current_cost_range["meal"]) * conversion_rate
        museum_cost = random.randint(*current_cost_range["attraction"]) * conversion_rate
        street_food_cost = random.randint(*current_cost_range["misc"]) * conversion_rate
        dinner_cost = random.randint(*current_cost_range["meal"]) * conversion_rate

        if "Shopping" in interests and budget_level == "Luxury":
            museum_cost += random.randint(20, 50) * conversion_rate
        
        # Rounding for clean display
        breakfast_cost = round(breakfast_cost / 5) * 5
        museum_cost = round(museum_cost / 5) * 5
        street_food_cost = round(street_food_cost / 5) * 5
        dinner_cost = round(dinner_cost / 5) * 5
        
        # Sum of costs for the day
        daily_sum = breakfast_cost + museum_cost + street_food_cost + dinner_cost
        total_daily_cost += daily_sum

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
            ],
            "daily_cost": daily_sum # Stored raw number for total calculation
        }
        itinerary.append(day_plan)
        
    # --- FINAL TOTAL CALCULATION ---
    total_travel_cost = total_daily_cost + total_flight_cost

    return itinerary, flight_details, total_travel_cost, budget_symbol


# 4. Data Converter for Text File (Download)
def convert_itinerary_to_text_content(itinerary_data, destination, flight_data, total_cost, budget_symbol):
    """Converts the itinerary, flight data, and total cost into a readable text format."""
    text_output = f"TRAVEL ITINERARY: {destination.upper()}\n"
    text_output += f"Generated On: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    # Add Flight Details
    text_output += "✈️ FLIGHT DETAILS ✈️\n"
    text_output += "--------------------------------------------------------\n"
    out = flight_data["outbound"]
    ret = flight_data["return"]
    
    text_output += f"OUTBOUND: {out['airline']} | {out['date']} @ {out['time']} | Price: {out['display_price']}\n"
    text_output += f"   -> Route: {out['from']} to {out['to']}\n"
    text_output += f"RETURN:   {ret['airline']} | {ret['date']} @ {ret['time']} | Price: {ret['display_price']}\n"
    text_output += f"   -> Route: {ret['from']} to {ret['to']}\n"
    text_output += "--------------------------------------------------------\n\n"
    
    # Add Daily Itinerary
    for day in itinerary_data:
        text_output += f"\n🗓️ DAY {day['day']}: {day['theme']} ({day['date']})\n"
        text_output += "--------------------------------------------------------\n"
        for act in day['activities']:
            text_output += f"{act['time']} | {act['cost']:<6} | {act['activity']}\n"
        text_output += f"Daily Cost: {budget_symbol} {day['daily_cost']}\n" # Include daily cost in download
        
    # Add Total Cost
    text_output += "\n========================================================\n"
    text_output += f"TOTAL ESTIMATED TRAVEL COST (Flights + Daily): {budget_symbol} {total_cost}\n"
    text_output += "========================================================\n"
        
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
            
            # Generate Data - Receives itinerary, flight details, and total cost
            itinerary_data, flight_details, total_cost, budget_symbol = generate_mock_itinerary(
                destination, start_date, duration, budget_level, currency, interests
            )
            st.session_state.itinerary = itinerary_data
            st.session_state.flights = flight_details
            st.session_state.total_cost = total_cost
            st.session_state.budget_symbol = budget_symbol
            st.session_state.display_budget = f"{budget_level} ({currency})"
    
    # Result Display (State 1)
    if "itinerary" in st.session_state:
        data = st.session_state.itinerary
        flights = st.session_state.flights
        total_cost = st.session_state.total_cost
        budget_symbol = st.session_state.budget_symbol

        st.header(f"✈️ Your Trip to {destination}")
        st.markdown(f"**Duration:** {duration} Days | **Budget:** {st.session_state.display_budget}")
        st.markdown("---")

        
        # --- FLIGHT DETAILS DISPLAY ---
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
                    <p>💵 **Price:** {flights['outbound']['display_price']}</p>
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
                    <p>💵 **Price:** {flights['return']['display_price']}</p>
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

        st.markdown("---")

        # --- TOTAL COST DISPLAY ---
        st.markdown(f"""
            <div class="total-cost-box">
                <p class="total-cost-label">ESTIMATED TOTAL TRIP COST</p>
                <p class="total-cost-value">{budget_symbol} {total_cost:,}</p>
                <p style="color:#888; font-size:0.9em;">(Flights + Estimated Daily Expenses)</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")


        # 7. Download Option 
        text_download_data = convert_itinerary_to_text_content(data, destination, flights, total_cost, budget_symbol)

        st.markdown("### 📥 Download Itinerary")
        
        st.download_button(
            label="Download Itinerary as Text", 
            data=text_download_data, 
            file_name=f"{destination}_itinerary.txt", 
            mime="text/plain", 
            use_container_width=True
        )

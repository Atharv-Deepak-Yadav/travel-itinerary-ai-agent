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

# Initialize session state for managing page view
if 'itinerary_generated' not in st.session_state:
    st.session_state.itinerary_generated = False
if 'itinerary_data' not in st.session_state:
    st.session_state.itinerary_data = None
if 'flight_data' not in st.session_state:
    st.session_state.flight_data = None
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = None
if 'budget_symbol' not in st.session_state:
    st.session_state.budget_symbol = None
if 'destination' not in st.session_state:
    st.session_state.destination = ""


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
    
    /* GUARANTEED FIX 1: Ensuring all input labels in the sidebar are white */
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    
    /* FIX 2: FORCEFULLY targeting the sidebar title to be white */
    [data-testid="stSidebar"] h1 {
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
    /* Welcome Page Styling */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding-top: 50px;
    }
    .welcome-title {
        font-size: 3.5em;
        font-weight: 800;
        color: #FF8F00;
        margin-bottom: 10px;
    }
    .welcome-subtitle {
        font-size: 1.5em;
        color: #A0A0A0;
        margin-bottom: 30px;
    }
    .welcome-feature {
        background-color: #1E1E1E;
        padding: 15px 30px;
        border-radius: 10px;
        margin: 10px;
        width: 300px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }
    .feature-icon {
        font-size: 1.5em;
        color: #FF4B4B;
        margin-right: 10px;
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
        # Round to the nearest 100 for Indian Rupees
        single_flight_price = round(raw_single_flight_price / 100) * 100
    else:
        # Round to the nearest 5 for US Dollars
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
            "display_price": f"{budget_symbol} {single_flight_price:,}"
        },
        "return": {
            "date": return_date.strftime("%b %d, %Y"),
            "time": "06:00 PM",
            "from": dest,
            "to": "Origin City",
            "airline": "AirGo",
            "price": single_flight_price, # Stored as raw number for total calculation
            "display_price": f"{budget_symbol} {single_flight_price:,}"
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
                {"time": "09:00 AM", "activity": f"Breakfast at {dest}'s famous cafe", "cost": f"{budget_symbol} {breakfast_cost:,}"},
                {"time": "11:00 AM", "activity": f"Visit the Top Museum in {dest}", "cost": f"{budget_symbol} {museum_cost:,}"},
                {"time": "01:30 PM", "activity": "Local Street Food Tour", "cost": f"{budget_symbol} {street_food_cost:,}"},
                {"time": "04:00 PM", "activity": "Relaxing walk through the city park", "cost": "Free"},
                {"time": "07:30 PM", "activity": "Dinner with a View", "cost": f"{budget_symbol} {dinner_cost:,}"},
            ],
            "daily_cost": round(daily_sum) # Stored raw number for total calculation
        }
        itinerary.append(day_plan)
        
    # --- FINAL TOTAL CALCULATION ---
    total_travel_cost = round(total_daily_cost + total_flight_cost)

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
    
    # Use the display_price which includes currency symbol and formatting
    text_output += f"OUTBOUND: {out['airline']} | {out['date']} @ {out['time']} | Price: {out['display_price']}\n"
    text_output += f"    -> Route: {out['from']} to {out['to']}\n"
    text_output += f"RETURN:    {ret['airline']} | {ret['date']} @ {ret['time']} | Price: {ret['display_price']}\n"
    text_output += f"    -> Route: {ret['from']} to {ret['to']}\n"
    text_output += "--------------------------------------------------------\n\n"
    
    # Add Daily Itinerary
    for day in itinerary_data:
        text_output += f"\n🗓️ DAY {day['day']}: {day['theme']} ({day['date']})\n"
        text_output += "--------------------------------------------------------\n"
        for act in day['activities']:
            # Align the cost column
            cost_str = act['cost'].ljust(10)
            text_output += f"{act['time']} | {cost_str} | {act['activity']}\n"
        # Format daily cost with commas
        text_output += f"Daily Cost: {budget_symbol} {day['daily_cost']:,}\n" 
        
    # Add Total Cost
    text_output += "\n========================================================\n"
    # Format total cost with commas
    text_output += f"TOTAL ESTIMATED TRAVEL COST (Flights + Daily): {budget_symbol} {total_cost:,}\n"
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
        # Default start date to today
        start_date = st.date_input("📅 Start Date", value=datetime.today().date())
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


# 6. Main Content Logic
def display_itinerary_page(itinerary, flights, total_cost, budget_symbol, dest):
    """Displays the generated itinerary and flight details."""
    st.markdown(f"## ✈️ Your {dest} Travel Plan")
    st.markdown("---")
    
    # --- FLIGHT DETAILS ---
    st.header("🛫 Flight Summary")
    
    col_out, col_ret = st.columns(2)
    
    # Outbound Flight
    with col_out:
        out = flights['outbound']
        st.markdown(f"""
        <div class="flight-card">
            <h4>Outbound: {out['from']} → {out['to']}</h4>
            <p><strong>Date:</strong> {out['date']}</p>
            <p><strong>Time:</strong> <span class="flight-time">{out['time']}</span></p>
            <p><strong>Airline:</strong> {out['airline']}</p>
            <p><strong>Estimated Price:</strong> <span style="font-size: 1.1em; color: #4CAF50;">{out['display_price']}</span></p>
        </div>
        """, unsafe_allow_html=True)

    # Return Flight
    with col_ret:
        ret = flights['return']
        st.markdown(f"""
        <div class="flight-card">
            <h4>Return: {ret['from']} → {ret['to']}</h4>
            <p><strong>Date:</strong> {ret['date']}</p>
            <p><strong>Time:</strong> <span class="flight-time">{ret['time']}</span></p>
            <p><strong>Airline:</strong> {ret['airline']}</p>
            <p><strong>Estimated Price:</strong> <span style="font-size: 1.1em; color: #4CAF50;">{ret['display_price']}</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- DAILY ITINERARY ---
    st.header("🗓️ Daily Itinerary")

    for day in itinerary:
        with st.container():
            st.markdown(f"### **Day {day['day']}** | {day['date']} - *{day['theme']}*")
            
            # Using columns for a cleaner, time-slot-based display
            for activity in day['activities']:
                col_time, col_act = st.columns([1, 4])
                
                with col_time:
                    st.markdown(f'<p class="time-slot">{activity["time"]}</p>', unsafe_allow_html=True)
                
                with col_act:
                    cost_tag = f'<span class="cost-tag">{activity["cost"]}</span>' if activity["cost"] != "Free" else '<span style="color:#A0A0A0; font-size: 0.9em;">Free</span>'
                    st.markdown(f"""
                    <div style="padding-bottom: 10px;">
                        <span class="activity-title">{activity["activity"]}</span>
                        {cost_tag}
                    </div>
                    """, unsafe_allow_html=True)

            # Optional: Display daily cost at the end of the day
            st.markdown(f'<div style="text-align: right; margin-top: 10px; border-top: 1px dashed #333; padding-top: 10px;">'
                        f'<strong>Estimated Daily Cost:</strong> <span style="color: #FF8F00; font-weight: bold;">{budget_symbol} {day["daily_cost"]:,}</span></div>', unsafe_allow_html=True)
            
            st.markdown("---") # Separator between days

    # --- TOTAL COST & DOWNLOAD ---
    col_total, col_download = st.columns([2, 1])

    with col_total:
        st.markdown(f"""
        <div class="total-cost-box">
            <p class="total-cost-label">TOTAL ESTIMATED TRAVEL COST</p>
            <p class="total-cost-value">{budget_symbol} {total_cost:,}</p>
            <p style="color:#A0A0A0; font-size: 0.8em; margin-top: 10px;">(Includes round-trip flights and estimated daily activity/food costs)</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_download:
        # Generate the file content for download
        file_content = convert_itinerary_to_text_content(itinerary, dest, flights, total_cost, budget_symbol)
        
        # Download button
        st.download_button(
            label="⬇️ Download Itinerary (TXT)",
            data=file_content,
            file_name=f"{dest.replace(' ', '_')}_Itinerary.txt",
            mime="text/plain",
            key="download_btn_main"
        )
        
        # Button to return to the welcome page and clear state
        if st.button("⬅️ Plan a New Trip", key="reset_btn_main"):
            st.session_state.itinerary_generated = False
            st.experimental_rerun() # Use rerun to update the view


def display_welcome_page():
    """Displays the initial welcome message."""
    st.markdown("""
    <div class="welcome-container">
        <h1 class="welcome-title">Travel Assistant Pro</h1>
        <p class="welcome-subtitle">Your AI-powered Itinerary Planner. Just tell us where and when!</p>
        
        <!-- Placeholder Image fixed to avoid string issues -->
        <img src="https://placehold.co/600x200/FF8F00/0E1117?text=Plan+Your+Next+Adventure" 
             style="border-radius: 10px; margin-bottom: 40px; box-shadow: 0 5px 15px rgba(255, 75, 75, 0.2);" 
             alt="Travel Planner Banner">

        <h3>Features</h3>
        <div style="display: flex; justify-content: center; flex-wrap: wrap;">
            <div class="welcome-feature">
                <span class="feature-icon">🗺️</span> Customized Routes
            </div>
            <div class="welcome-feature">
                <span class="feature-icon">💵</span> Budget-Aware Cost Estimates
            </div>
            <div class="welcome-feature">
                <span class="feature-icon">💡</span> Interest-Based Suggestions
            </div>
        </div>
        <p style="margin-top: 30px; font-size: 1.1em; color: #707070;">
            Fill out the details in the sidebar and click the button to generate your dream trip now!
        </p>
    </div>
    """, unsafe_allow_html=True)


# 7. Execution Flow
if generate_btn:
    # 1. Input Validation
    if not destination:
        st.error("Please enter a destination to start planning!")
    elif start_date < datetime.today().date():
        st.error("The start date must be today or a future date.")
    else:
        # Reset flag and set state to show generated content
        st.session_state.itinerary_generated = True
        st.session_state.destination = destination
        
        # 2. Show spinner/loading message
        with st.spinner(f"Crafting the perfect trip to {destination}..."):
            # Simulate processing time
            time.sleep(random.uniform(2, 4)) 
            
            # 3. Generate data
            itinerary_data, flight_data, total_cost, budget_symbol = generate_mock_itinerary(
                destination, start_date, duration, budget_level, currency, interests
            )
            
            # 4. Store data in session state
            st.session_state.itinerary_data = itinerary_data
            st.session_state.flight_data = flight_data
            st.session_state.total_cost = total_cost
            st.session_state.budget_symbol = budget_symbol

# Display the content based on state
if st.session_state.itinerary_generated and st.session_state.itinerary_data:
    # Display the generated itinerary
    display_itinerary_page(
        st.session_state.itinerary_data,
        st.session_state.flight_data,
        st.session_state.total_cost,
        st.session_state.budget_symbol,
        st.session_state.destination
    )
else:
    # Display the Welcome Page (default view)
    display_welcome_page()

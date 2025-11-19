import os, json, time
import streamlit as st
from datetime import datetime, timedelta
from dateutil import parser
import random 
import requests

# --- Configuration ---
st.set_page_config(page_title="Travel Itinerary Planner (Colab POV)", layout="wide")
st.title("✈️ Travel Itinerary Planner — Prototype (Colab)")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Traveler preferences")
    name = st.text_input("Name", value="Traveler")
    destination = st.text_input("Destination (city / country)", value="Paris, France")
    start_date = st.date_input("Start date", value=datetime.now().date())
    trip_days = st.slider("Trip length (days)", 1, 14, 3)
    budget = st.number_input("Total budget (approx, in USD)", min_value=1, value=800)
    interests = st.multiselect("Interests", ["Museums","Food","History","Walking tours","Nightlife","Nature","Shopping","Beaches"], default=["Food", "Nature"])
    include_maps = st.checkbox("Include map links / simple routes", value=True)
    use_real_crewai = st.checkbox("Use CrewAI AMP (requires API key + endpoint)", value=False)
    crewai_endpoint = st.text_input("CrewAI AMP kickoff URL (if using)", value="")
    crewai_api_key = st.text_input("CrewAI API key (if using)", value="", type="password")
    run_button = st.button("Generate itinerary")

# --- Mock Crew Function ---
def mock_run_crew(inputs):
    destination = inputs["destination"]
    start = parser.isoparse(inputs["start_date"]).date()
    days = []
    
    available_interests = inputs['interests'][:]
    
    activity_map = {
        "Museums": "Visit the city's premier art or science museum",
        "Food": "Try a highly-rated local restaurant for lunch",
        "History": "Tour the main historical site/fortress",
        "Walking tours": "Take a guided walking tour of the Old Town",
        "Nightlife": "Explore the local bar or nightlife district",
        "Nature": "Hike or visit the nearest nature park/scenic view",
        "Shopping": "Explore the main commercial and shopping area",
        "Beaches": "Spend the afternoon relaxing at the best nearby beach"
    }

    if "Food" not in available_interests:
        available_interests.append("Food")

    for d in range(inputs["trip_days"]):
        day_date = (start + timedelta(days=d)).isoformat()
        acts = []
        
        # 1. Morning Attraction (Cycle through interests)
        main_interest_key = available_interests.pop(0) 
        available_interests.append(main_interest_key)
        activity_title = activity_map.get(main_interest_key, f"Explore a major landmark related to {main_interest_key}")
        acts.append({"time":"09:00","title": activity_title,"duration": "2.5h","estimated_cost": random.randint(15, 30)})
            
        # 2. Lunch 
        acts.append({"time":"12:30","title":"Local lunch (recommendations for a regional dish)","duration":"1.5h","estimated_cost":random.randint(15, 25)})
        
        # 3. Afternoon Secondary Activity 
        secondary_interest_key = random.choice([i for i in available_interests if i != main_interest_key and i != "Food"]) if len(available_interests) > 1 else "Walking tours"
        secondary_title = activity_map.get(secondary_interest_key, "Explore local markets or public squares")
        acts.append({"time":"14:30","title": secondary_title,"duration":"2h","estimated_cost": random.randint(0, 15)})
            
        # 4. Evening Activity
        evening_activity = "Dinner at a recommended local spot"
        if "Nightlife" in inputs['interests']:
             evening_activity = "Explore the local bar or nightlife district"
             
        acts.append({"time":"18:00","title":evening_activity,"duration":"3h","estimated_cost":random.randint(15, 40)})
        
        days.append({"date":day_date,"summary":f"Exploring {main_interest_key} and local culture","activities":acts})
        
    estimated_total_cost = sum(a["estimated_cost"] for day in days for a in day["activities"])
    
    # --- MOCK FLIGHT DETAILS ADDED HERE ---
    start_date_obj = parser.isoparse(inputs["start_date"]).date()
    return_date_obj = start_date_obj + timedelta(days=inputs["trip_days"] - 1)
    
    plan = {
        "traveler":inputs["traveler_name"],
        "destination":destination,
        "start_date":inputs["start_date"],
        "trip_days": inputs["trip_days"], # Added for easy display
        "days":days,
        "estimated_total": estimated_total_cost + 400, # Add a buffer for flights
        "flights": {
            "outbound": {
                "time": "08:30 AM",
                "date": start_date_obj.isoformat(),
                "airline": "AirGo",
                "price": random.randint(200, 350)
            },
            "return": {
                "time": "06:00 PM",
                "date": return_date_obj.isoformat(),
                "airline": "AirGo",
                "price": random.randint(200, 350)
            }
        }
    }
    return plan

# --- CrewAI AMP Function ---
def run_crew_via_amp(inputs, endpoint, api_key):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"crew":"travel-itinerary-crew", "inputs": inputs}
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()

# --- Planner Run Logic ---
if run_button:
    st.info("Composing inputs and running planner (mock or CrewAI)...")
    inputs = {
        "traveler_name": name,
        "destination": destination,
        "start_date": start_date.isoformat(),
        "trip_days": trip_days,
        "budget_usd": float(budget),
        "interests": interests,
        "include_maps": include_maps
    }

    try:
        if use_real_crewai and crewai_endpoint and crewai_api_key:
            st.write("Calling CrewAI AMP endpoint...")
            result = run_crew_via_amp(inputs, crewai_endpoint, crewai_api_key)
            st.success("CrewAI responded — parsing plan (this demo expects final plan in response).")
            plan = result.get("plan") or result
        else:
            st.write("Using local mock planner for quick demo.")
            plan = mock_run_crew(inputs)

        st.session_state['last_plan'] = plan
    except Exception as e:
        st.error(f"Planner failed: {e}")

# --- Output Display ---
if 'last_plan' in st.session_state and st.session_state['last_plan']:
    plan = st.session_state['last_plan']
    
    # --- 1. Main Header ---
    st.markdown("## ✈️ Your Trip to")
    st.subheader(f"{plan.get('destination')} 🗺️")
    st.markdown(f"**Duration:** {plan['trip_days']} Days | **Budget:** ${int(plan.get('budget_usd', 0))} | **Estimated Total:** ${plan.get('estimated_total', 'TBD')}")
    st.markdown("---")

    # --- 2. Flight Details (Mock Cards using Columns) ---
    st.markdown("### 🛫 Flight Details")
    
    # Use two columns to create the card layout for flights
    col_out, col_return = st.columns(2)
    
    # Using st.container for a visual grouping (acts like a card wrapper)
    with col_out:
        with st.container(border=True):
            st.markdown(f"**Outbound Flight**")
            st.markdown(f"**🕒 {plan['flights']['outbound']['time']}** - {plan['flights']['outbound']['date']}")
            st.markdown(f"✈️ {plan['flights']['outbound']['airline']}")
            st.markdown(f"📍 Origin City → {plan['destination']}")
            st.markdown(f"💰 **Price:** ${plan['flights']['outbound']['price']}")

    with col_return:
        with st.container(border=True):
            st.markdown(f"**Return Flight**")
            st.markdown(f"**🕒 {plan['flights']['return']['time']}** - {plan['flights']['return']['date']}")
            st.markdown(f"✈️ {plan['flights']['return']['airline']}")
            st.markdown(f"📍 {plan['destination']} → Origin City")
            st.markdown(f"💰 **Price:** ${plan['flights']['return']['price']}")

    st.markdown("---")

    # --- 3. Daily Itinerary (Clean List) ---
    st.markdown("### 🗓️ Daily Itinerary")

    for day in plan["days"]:
        # Day Header with Date and Summary
        st.markdown(f"#### 📅 {day['date']} — {day['summary']}")
        
        # Display activities in aligned columns
        for a in day["activities"]:
            # Create three columns for Time, Activity/Title, and Cost
            col_time, col_activity, col_cost = st.columns([1, 4, 1])
            
            # Time (First column)
            col_time.markdown(f"**{a['time']}**")

            # Activity (Second/Main column)
            activity_line = f"**{a['title']}** ({a['duration']})"
            if include_maps:
                q = f"{a['title']} {plan['destination']}"
                maps = f"https://www.google.com/maps/search/{requests.utils.quote(q)}"
                activity_line += f" [map]({maps})"
            col_activity.markdown(activity_line)

            # Cost (Third column, aligned right using simple HTML for alignment)
            cost_display = "Free" if a['estimated_cost'] <= 0 else f"${a['estimated_cost']}"
            col_cost.markdown(f'<div style="text-align: right;">{cost_display}</div>', unsafe_allow_html=True)
        
        # Add a clear separator after each day's schedule
        st.markdown("---") 

    # --- 4. Download Button ---
    st.markdown("### ⬇️ Download Itinerary")
    st.download_button("Download itinerary (JSON)", data=json.dumps(plan, indent=2), file_name="itinerary.json", mime="application/json")
    st.caption("Demo: replace mock_run_crew with real CrewAI AMP calls and parse the crew's output format.")

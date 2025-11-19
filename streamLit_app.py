import os, json, time
import streamlit as st
from datetime import datetime, timedelta
from dateutil import parser
import random 
import requests

st.set_page_config(page_title="Travel Itinerary Planner (Colab POV)", layout="wide")
st.title("✈️ Travel Itinerary Planner — Prototype (Colab)")

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

def mock_run_crew(inputs):
    # Simple mock planner that builds an itinerary from interests
    destination = inputs["destination"]
    start = parser.isoparse(inputs["start_date"]).date()
    days = []
    
    # Cycle through interests for varied activities
    available_interests = inputs['interests'][:] # Copy the list to modify/cycle
    
    # Map interests to specific activities (to avoid just repeating the interest name)
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

    # Ensure Food is always a high priority for at least one activity
    if "Food" not in available_interests:
        available_interests.append("Food")

    for d in range(inputs["trip_days"]):
        day_date = (start + timedelta(days=d)).isoformat()
        acts = []
        
        # 1. Morning Attraction (Cycle through interests)
        if available_interests:
            # Pick a unique interest for the main attraction
            main_interest_key = available_interests.pop(0) 
            available_interests.append(main_interest_key) # Put it back at the end
            
            activity_title = activity_map.get(main_interest_key, f"Explore a major landmark related to {main_interest_key}")
            acts.append({
                "time":"09:00",
                "title": activity_title,
                "duration": "2.5h",
                "estimated_cost": random.randint(15, 30) # Random cost
            })
        else:
            # Fallback if no interests are selected
            acts.append({"time":"09:00","title":f"Visit a major City Landmark in {destination}","duration":"2h","estimated_cost":20})
            
        # 2. Lunch (Always Food)
        acts.append({"time":"12:30","title":"Local lunch (recommendations for a regional dish)","duration":"1.5h","estimated_cost":random.randint(15, 25)})
        
        # 3. Afternoon Secondary Activity (Try another interest or default to general)
        secondary_interest_key = random.choice([i for i in available_interests if i != main_interest_key and i != "Food"]) if len(available_interests) > 1 else "Walking tours"
        
        secondary_title = activity_map.get(secondary_interest_key, "Explore local markets or public squares")
        
        acts.append({
            "time":"14:30",
            "title": secondary_title,
            "duration":"2h",
            "estimated_cost": random.randint(0, 15) # Free or small fee
        })
            
        # 4. Optional Evening Activity
        evening_activity = "Dinner at a recommended local spot"
        if "Nightlife" in inputs['interests']:
             evening_activity = "Explore the local bar or nightlife district"
             
        acts.append({"time":"18:00","title":evening_activity,"duration":"3h","estimated_cost":random.randint(15, 40)})
        
        
        days.append({"date":day_date,"summary":f"Day {d+1}: Focused on {main_interest_key} and {secondary_interest_key}","activities":acts})
        
    estimated_total_cost = sum(a["estimated_cost"] for day in days for a in day["activities"])
    
    plan = {
        "traveler":inputs["traveler_name"],
        "destination":destination,
        "start_date":inputs["start_date"],
        "days":days,
        "estimated_total": estimated_total_cost
    }
    return plan

def run_crew_via_amp(inputs, endpoint, api_key):
    # Example HTTP template — adapt per CrewAI AMP docs
    # This function expects the AMP endpoint to accept a JSON payload:
    # { "inputs": {...}, "crew": "travel-itinerary-crew" } and respond with a kickoff id or final plan.
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"crew":"travel-itinerary-crew", "inputs": inputs}
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()

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
            # Expect result to include final plan; if Kickoff ID returned, you'd poll or receive webhook.
            st.success("CrewAI responded — parsing plan (this demo expects final plan in response).")
            plan = result.get("plan") or result  # adapt to your AMP response format
        else:
            st.write("Using local mock planner for quick demo.")
            plan = mock_run_crew(inputs)

        st.session_state['last_plan'] = plan
    except Exception as e:
        st.error(f"Planner failed: {e}")

if 'last_plan' in st.session_state and st.session_state['last_plan']:
    plan = st.session_state['last_plan']
    st.header(f"Plan for {plan.get('traveler','Traveler')} — {plan.get('destination')}")
    st.markdown(f"**Start:** {plan['start_date']}  —  **Estimated total:** ${plan.get('estimated_total','TBD')}")
    for day in plan["days"]:
        with st.expander(f"{day['date']} — {day['summary']}"):
            for a in day["activities"]:
                line = f"{a['time']} — **{a['title']}** ({a['duration']}) — Est. ${a['estimated_cost']}"
                # include a maps link if requested — simple Google Maps search
                if include_maps:
                    q = f"{a['title']} {plan['destination']}"
                    maps = f"https://www.google.com/maps/search/{requests.utils.quote(q)}"
                    line += f"  [map]({maps})"
                st.markdown(line, unsafe_allow_html=True)

    st.download_button("Download itinerary (JSON)", data=json.dumps(plan, indent=2), file_name="itinerary.json", mime="application/json")
    st.caption("Demo: replace mock_run_crew with real CrewAI AMP calls and parse the crew's output format.")

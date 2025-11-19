import streamlit as st
from datetime import datetime, timedelta
import time
import pandas as pd
import io # Needed for file buffer operations

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
        color: #FFFFFF !important; /* Force white color for general sidebar text */
    }
    
    /* Ensuring all input labels in the sidebar are white */
    .stTextInput label, .stDateInput label, .stNumberInput label, .stSelectbox label, .stMultiSelect label, 
    [data-testid="stSidebar"] .stTitle {
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
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
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

# 3. Helper Function: Mock Data Generator
def generate_mock_itinerary(dest, days, interests):
    # This simulates the JSON output your CrewAI agent will eventually generate
    itinerary = []
    current_date = datetime.now()
    
    for i in range(1, days + 1):
        day_plan = {
            "day": i,
            "date": (current_date + timedelta(days=i)).strftime("%B %d"),
            "theme": f"Exploring {interests[0] if interests else 'Culture'} & Local Gems",
            "activities": [
                {"time": "09:00 AM", "activity": f"Breakfast at {dest}'s famous cafe", "cost": "$20"},
                {"time": "11:00 AM", "activity": f"Visit the Top Museum in {dest}", "cost": "$45"},
                {"time": "01:30 PM", "activity": "Local Street Food Tour", "cost": "$30"},
                {"time": "04:00 PM", "activity": f"Relaxing walk through the city park", "cost": "Free"},
                {"time": "07:30 PM", "activity": "Dinner with a View", "cost": "$60"},
            ]
        }
        itinerary.append(day_plan)
    return itinerary

# 4. NEW Helper Function: Data Converters for Downloads

def convert_itinerary_to_markdown(itinerary_data, destination):
    """Converts the itinerary JSON structure to a readable Markdown/TXT format."""
    markdown_output = f"# ✈️ Itinerary for {destination}\n\n"
    markdown_output += f"**Generated On:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n"
    
    for day in itinerary_data:
        markdown_output += f"## 🗓️ Day {day['day']}: {day['theme']} ({day['date']})\n\n"
        for act in day['activities']:
            markdown_output += f"* **{act['time']}**: {act['activity']} ({act['cost']})\n"
        markdown_output += "\n---\n"
        
    return markdown_output

def convert_itinerary_to_csv(itinerary_data):
    """Converts the itinerary JSON structure to a DataFrame for CSV download."""
    rows = []
    for day in itinerary_data:
        for act in day['activities']:
            rows.append({
                "Day": day['day'],
                "Date": day['date'],
                "Theme": day['theme'],
                "Time": act['time'],
                "Activity": act['activity'],
                "Cost": act['cost']
            })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode('utf-8')


# 5. Sidebar - User Inputs
with st.sidebar:
    # Ensure the title and all subsequent text/labels are white via CSS above
    st.title("🌍 AI Travel Agent")
    st.markdown("---")
    
    # Inputs
    destination = st.text_input("📍 Destination", placeholder="e.g., Paris, Tokyo, New York")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 Start Date")
    with col2:
        duration = st.number_input("🌙 Days", min_value=1, max_value=30, value=3)
        
    budget = st.selectbox("💰 Budget Level", ["Budget ($)", "Moderate ($$)", "Luxury ($$$)"])
    
    interests = st.multiselect(
        "❤️ Interests",
        ["History", "Art", "Food", "Nature", "Shopping", "Nightlife", "Adventure"],
        default=["Food", "Nature"]
    )
    
    st.markdown("---")
    
    # The "Magic" Button
    generate_btn = st.button("✨ Generate Itinerary")

# 6. Main Content Area
if not generate_btn and "itinerary" not in st.session_state:
    # Welcome Screen (State 0)
    st.header("Welcome to your Personal Travel Agent")
    st.markdown("""
    This AI Agent will curate a perfect trip for you based on your preferences.
    
    **How it works:**
    1. Enter your destination and dates.
    2. Select your budget and interests.
    3. Click **Generate** and watch the AI plan your trip.
    """)
    st.info("👈 Start by filling out the details in the sidebar!")

else:
    # Loading State
    if generate_btn:
        with st.spinner(f"🤖 AI Agents are researching {destination}..."):
            # Simulate processing time for effect
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Generate Data (Mock for now, real CrewAI later)
            st.session_state.itinerary = generate_mock_itinerary(destination, duration, interests)
    
    # Result Display (State 1)
    if "itinerary" in st.session_state:
        data = st.session_state.itinerary
        
        st.header(f"✈️ Your Trip to {destination}")
        st.markdown(f"**Duration:** {duration} Days | **Budget:** {budget}")
        st.markdown("---")

        # Display Day by Day cards
        for day in data:
            with st.container():
                # We use HTML to make it look like the "Second Photo" cards
                st.markdown(f"""
                <div class="day-card">
                    <h3 style="margin-top:0;">🗓️ Day {day['day']}: {day['theme']}</h3>
                    <p style="color:#888; margin-bottom:15px;">{day['date']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Activity Timeline using standard Streamlit columns for alignment
                for act in day['activities']:
                    c1, c2, c3 = st.columns([2, 6, 2])
                    with c1:
                        st.markdown(f"<span class='time-slot'>{act['time']}</span>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<span class='activity-title'>{act['activity']}</span>", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"<span class='cost-tag'>{act['cost']}</span>", unsafe_allow_html=True)
                    st.divider()

        # 7. Download Options (FIXED)
        
        # Prepare data for download
        markdown_data = convert_itinerary_to_markdown(data, destination)
        csv_data = convert_itinerary_to_csv(data)

        st.markdown("### 📥 Download Options")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.download_button(
                label="Download as Text (.md)", 
                data=markdown_data, 
                file_name=f"{destination}_itinerary.md",
                mime="text/markdown"
            )
        
        with c2:
            st.download_button(
                label="Download as CSV", 
                data=csv_data, 
                file_name=f"{destination}_itinerary.csv",
                mime="text/csv"
            )
            
        with c3:
            # We can't generate a true ICS file easily without more data/logic, 
            # so we offer a simple text list of activities as a 'calendar helper'.
            st.download_button(
                label="Download Activity List",
                data=markdown_data, # Reusing markdown for simplicity
                file_name=f"{destination}_activities.txt",
                mime="text/plain"
            )

import streamlit as st
from datetime import datetime, timedelta
import time
import pandas as pd
import io 
from fpdf import FPDF # We import this as a placeholder, but we will use text content below

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
    /* FIX: Remove white hover effect on the custom-styled button */
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        /* The key is to override Streamlit's default hover styles for 'secondary' buttons.
        Since we gave it a strong background, we set the background on hover to be the same 
        or slightly darker gradient to hide the white.
        */
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

# 3. Helper Function: Mock Data Generator
def generate_mock_itinerary(dest, days, interests):
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

# 4. NEW Helper Function: Data Converter for PDF (Text Content)

def convert_itinerary_to_pdf_content(itinerary_data, destination):
    """Converts the itinerary data into a readable text/markdown format, 
       which will be saved as a .pdf file."""
    text_output = f"TRAVEL ITINERARY: {destination.upper()}\n"
    text_output += f"Generated On: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text_output += "--------------------------------------------------------\n"
    
    for day in itinerary_data:
        text_output += f"\nDAY {day['day']}: {day['theme']} ({day['date']})\n"
        text_output += "--------------------------------------------------------\n

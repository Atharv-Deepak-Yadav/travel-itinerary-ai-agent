import streamlit as st

# Dark theme styling
st.set_page_config(page_title="Travel Itinerary Planner", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #0d0d0d;
        }
        .title {
            color: #ff6600;
            font-size: 40px;
            font-weight: bold;
            text-align: center;
        }
        .section-title {
            color: #ff6600;
            font-size: 22px;
            margin-bottom: 10px;
        }
        .result-box {
            background-color: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            color: white;
            border: 1px solid #ff6600;
        }
        .input-box {
            background-color: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            color: white;
            border: 1px solid #ff6600;
        }
        .stTextInput>div>div>input {
            background-color: #262626;
            color: white;
        }
        .stTextArea textarea {
            background-color: #262626;
            color: white;
        }
        .stButton>button {
            background-color: #ff6600;
            color: black;
            border-radius: 5px;
            font-size: 18px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Travel Itinerary Planner</div>', unsafe_allow_html=True)
st.write("")

# Layout into 2 columns
col1, col2 = st.columns([1, 1.2])

# Left column inputs
with col1:
    st.markdown('<div class="section-title">Enter your travel details</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="input-box">', unsafe_allow_html=True)

        city = st.text_input("Enter the city for your trip")
        interests = st.text_area("Enter your interests (comma-separated)")

        col_btn1, col_btn2 = st.columns(2)

        if col_btn1.button("Clear"):
            st.experimental_rerun()

        generate = col_btn2.button("Submit")

        st.markdown('</div>', unsafe_allow_html=True)

# Right column output
with col2:
    st.markdown('<div class="section-title">Generated Itinerary</div>', unsafe_allow_html=True)

    st.markdown('<div class="result-box">', unsafe_allow_html=True)

    if generate:
        # SAMPLE RESPONSE (Replace with your AI agent output)
        itinerary = f"""
### Here's your personalized itinerary for **{city}**:

- **8:00 AM:** Visit the Ram Janmabhoomi Temple — sacred birthplace of Lord Rama.  
- **10:00 AM:** Explore Hanuman Garhi, one of the oldest temples dedicated to Lord Hanuman.  
- **12:30 PM:** Enjoy authentic Ayodhya lunch at a local restaurant.  
- **2:00 PM:** Visit nearby ghats and temples based on your interests:  
  - {interests}
- **4:00 PM:** Sunset at Saryu River + local shopping.

✨ This itinerary covers culture, spirituality, food & sightseeing.
        """

        st.markdown(itinerary)

    st.markdown('</div>', unsafe_allow_html=True)

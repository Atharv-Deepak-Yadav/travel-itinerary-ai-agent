import streamlit as st

st.title("Travel Itinerary Planner AI")

destination = st.text_input("Enter destination")
budget = st.number_input("Enter your budget")
interests = st.text_area("Enter interests (beaches, nightlife, temples...)")

if st.button("Generate Itinerary"):
    st.write("### Your Itinerary")
    st.write("Destination:", destination)
    st.write("Budget:", budget)
    st.write("Interests:", interests)

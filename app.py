import streamlit as st
from streamlit_js_eval import get_geolocation

st.title("Location Test")

# Diagnostic button
if st.button("TEST: Get Location"):
    st.write("Button clicked! Requesting location...")
    
    try:
        location = get_geolocation()
        st.write("Raw location data:")
        st.write(location)
        
        if location and 'coords' in location:
            st.success(f"Location found! {location['coords']['latitude']}, {location['coords']['longitude']}")
        else:
            st.error("No location data received")
    except Exception as e:
        st.error(f"Error: {e}")

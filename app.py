import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

st.title("Simple Location App")

# Initialize session state
if 'location_data' not in st.session_state:
    st.session_state.location_data = None

# Button to get location
if st.button("Get My Location"):
    with st.spinner("Getting your location..."):
        location_data = get_geolocation()
        if location_data and 'coords' in location_data:
            st.session_state.location_data = location_data
        else:
            st.warning("Please allow location access in your browser.")

# Display location and download button if we have the data
if st.session_state.location_data and 'coords' in st.session_state.location_data:
    coords = st.session_state.location_data['coords']
    latitude = coords['latitude']
    longitude = coords['longitude']
    
    st.success(f"Location: {latitude:.6f}, {longitude:.6f}")
    
    # Create CSV for download
    df = pd.DataFrame({
        'Latitude': [latitude],
        'Longitude': [longitude],
        'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="my_location.csv",
        mime="text/csv"
    )

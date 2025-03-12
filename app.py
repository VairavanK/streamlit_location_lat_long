import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from streamlit_js_eval import get_geolocation

st.title("Get Your Current Location")

# Function to create a download link for CSV
def get_csv_download_link(df, filename="location_data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'

if st.button("Get My Location"):
    with st.spinner("Requesting your location..."):
        # Use get_geolocation from streamlit-js-eval
        loc = get_geolocation()
        
        if loc:
            st.success("Location retrieved successfully!")
            lat = loc['coords']['latitude']
            lng = loc['coords']['longitude']
            
            st.write(f"Latitude: {lat}")
            st.write(f"Longitude: {lng}")
            
            # Create DataFrame for download
            location_df = pd.DataFrame({
                'Latitude': [lat],
                'Longitude': [lng],
                'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            })
            
            st.markdown("### Download Your Location Data")
            st.markdown(get_csv_download_link(location_df), unsafe_allow_html=True)
        else:
            st.warning("Waiting for location data. Please allow location access if prompted.")

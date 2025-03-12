import streamlit as st
import pandas as pd
from streamlit_js_eval import get_geolocation

st.title("Simple Location App")

# Function to create CSV download
def create_csv(lat, lng):
    import pandas as pd
    from datetime import datetime
    
    df = pd.DataFrame({
        'Latitude': [lat],
        'Longitude': [lng],
        'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="my_location.csv",
        mime="text/csv"
    )

# Button to get location
if st.button("Get My Location"):
    with st.spinner("Getting your location..."):
        # This uses streamlit-js-eval to handle the JavaScript-to-Python communication
        loc = get_geolocation()
        
        if loc and 'coords' in loc:
            st.success("Location obtained!")
            lat = loc['coords']['latitude']
            lng = loc['coords']['longitude']
            
            # Display the coordinates
            st.write(f"Latitude: {lat}")
            st.write(f"Longitude: {lng}")
            
            # Create download button
            create_csv(lat, lng)
        else:
            st.error("Could not get location. Please ensure you've granted location permissions.")

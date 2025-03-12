import streamlit as st
import pandas as pd
import base64
from datetime import datetime

st.title("Get Your Current Location")

# Define session state variables if they don't exist
if 'latitude' not in st.session_state:
    st.session_state.latitude = None
if 'longitude' not in st.session_state:
    st.session_state.longitude = None
if 'location_retrieved' not in st.session_state:
    st.session_state.location_retrieved = False

# JavaScript to get location and store it in session state
location_js = """
<script>
document.getElementById('get_location_button').addEventListener('click', function() {
    if (navigator.geolocation) {
        document.getElementById('location_status').textContent = "Getting location...";
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                
                // Display in the HTML
                document.getElementById('lat_display').textContent = lat;
                document.getElementById('lng_display').textContent = lng;
                document.getElementById('location_status').textContent = "Location retrieved successfully!";
                
                // Send to Python through form submission
                document.getElementById('lat_input').value = lat;
                document.getElementById('lng_input').value = lng;
                document.getElementById('location_form').submit();
            },
            function(error) {
                document.getElementById('location_status').textContent = "Error: " + error.message;
            }
        );
    } else {
        document.getElementById('location_status').textContent = "Geolocation not supported by this browser.";
    }
});
</script>
"""

# Create a form to handle the location data
html_form = f"""
<form id="location_form" action="" method="POST" target="_self">
    <input type="hidden" id="lat_input" name="lat" value="">
    <input type="hidden" id="lng_input" name="lng" value="">
    <button type="button" id="get_location_button">Get My Location</button>
    <p id="location_status"></p>
    <div>
        <p>Latitude: <span id="lat_display">Not yet retrieved</span></p>
        <p>Longitude: <span id="lng_display">Not yet retrieved</span></p>
    </div>
</form>
{location_js}
"""

st.components.v1.html(html_form, height=200)

# Check for query parameters from the form submission
# Using st.query_params instead of deprecated st.experimental_get_query_params
query_params = st.query_params
if "lat" in query_params and "lng" in query_params:
    try:
        st.session_state.latitude = float(query_params["lat"])
        st.session_state.longitude = float(query_params["lng"])
        st.session_state.location_retrieved = True
        # Clear the query parameters to avoid reloading issues
        # Using the non-deprecated method to set query params
        st.query_params.clear()
    except ValueError:
        st.error("Invalid coordinates received")

# Function to create a download link for CSV
def get_csv_download_link(df, filename="location_data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'

# Display location and provide download option
if st.session_state.location_retrieved:
    st.success("Location data successfully retrieved!")
    st.write(f"Latitude: {st.session_state.latitude}")
    st.write(f"Longitude: {st.session_state.longitude}")
    
    if st.button("Download as CSV"):
        # Create DataFrame with the location data
        location_df = pd.DataFrame({
            'Latitude': [st.session_state.latitude],
            'Longitude': [st.session_state.longitude],
            'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        # Provide download link
        st.markdown(get_csv_download_link(location_df), unsafe_allow_html=True)
else:
    st.info("Please click 'Get My Location' to retrieve your current coordinates.")

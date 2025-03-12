import streamlit as st
import pandas as pd
import base64
from datetime import datetime

st.title("Get Your Current Location")

# Initialize session state variables
if 'latitude' not in st.session_state:
    st.session_state.latitude = None
if 'longitude' not in st.session_state:
    st.session_state.longitude = None
if 'location_obtained' not in st.session_state:
    st.session_state.location_obtained = False

# Function to create download link for CSV
def get_csv_download_link(df, filename="my_location.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return href

# Create container for location info
location_container = st.container()

# Create button to get location
if st.button("Get My Location"):
    # This will run JavaScript to get location and display in a div with id 'location-data'
    # The div will have data attributes we can parse later
    st.components.v1.html("""
    <div id="location-display"></div>
    <div id="location-data" data-lat="" data-lng=""></div>
    
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            document.getElementById('location-display').innerHTML = "Getting your location...";
            
            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                
                // Display the location
                document.getElementById('location-display').innerHTML = 
                    "<p>Your location:</p>" + 
                    "<p>Latitude: " + lat + "</p>" +
                    "<p>Longitude: " + lng + "</p>";
                
                // Store values in data attributes
                var locData = document.getElementById('location-data');
                locData.setAttribute('data-lat', lat);
                locData.setAttribute('data-lng', lng);
                
                // We need to signal to the Python code that we have the location
                // Since Streamlit doesn't automatically detect DOM changes,
                // we'll submit a form to update the page with the location data
                var form = document.createElement('form');
                form.method = 'GET';
                form.action = '';
                
                var latInput = document.createElement('input');
                latInput.type = 'hidden';
                latInput.name = 'lat';
                latInput.value = lat;
                form.appendChild(latInput);
                
                var lngInput = document.createElement('input');
                lngInput.type = 'hidden';
                lngInput.name = 'lng';
                lngInput.value = lng;
                form.appendChild(lngInput);
                
                document.body.appendChild(form);
                form.submit();
            }, function(error) {
                document.getElementById('location-display').innerHTML = 
                    "Error getting location: " + error.message;
            });
        } else {
            document.getElementById('location-display').innerHTML = 
                "Geolocation is not supported by this browser.";
        }
    }
    
    // Run immediately
    getLocation();
    </script>
    """, height=150)

# Check for query parameters
query_params = st.query_params
if 'lat' in query_params and 'lng' in query_params:
    try:
        lat = float(query_params['lat'])
        lng = float(query_params['lng'])
        
        # Store in session state
        st.session_state.latitude = lat
        st.session_state.longitude = lng
        st.session_state.location_obtained = True
        
        # Clear query parameters
        st.query_params.clear()
    except:
        st.error("Invalid location data received")

# Display location and download button if we have the coordinates
if st.session_state.location_obtained:
    # Display the coordinates
    location_container.success("Location successfully obtained!")
    location_container.write(f"Latitude: {st.session_state.latitude}")
    location_container.write(f"Longitude: {st.session_state.longitude}")
    
    # Create DataFrame for CSV
    df = pd.DataFrame({
        'Latitude': [st.session_state.latitude],
        'Longitude': [st.session_state.longitude],
        'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    
    # Download button
    if st.button("Generate CSV Download Link"):
        st.markdown(get_csv_download_link(df), unsafe_allow_html=True)
else:
    location_container.info("Click 'Get My Location' to detect your current location.")

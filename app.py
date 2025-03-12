import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.title("Get My Current Location")

# Function to create a downloadable CSV
def create_csv_download_link(df):
    csv = df.to_csv(index=False)
    # Use Streamlit's built-in download button
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="my_location.csv",
        mime="text/csv"
    )

# Container for location result
location_display = st.container()

if st.button("Get My Location"):
    # Simple container to display coordinates
    with location_display:
        with st.spinner("Getting your location..."):
            # Insert JavaScript to get the location
            js_code = """
            <div id="location-result">Detecting location...</div>
            
            <script>
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        // Success
                        document.getElementById('location-result').innerHTML = 
                            '<p>Location found:</p>' +
                            '<p>Latitude: <span id="lat">' + position.coords.latitude + '</span></p>' +
                            '<p>Longitude: <span id="lng">' + position.coords.longitude + '</span></p>';
                            
                        // Store in localStorage for streamlit to access
                        localStorage.setItem('user_lat', position.coords.latitude);
                        localStorage.setItem('user_lng', position.coords.longitude);
                        
                        // Signal that location is ready by changing URL hash
                        window.location.hash = 'location-ready';
                    },
                    function(error) {
                        // Error
                        document.getElementById('location-result').innerHTML = 
                            '<p>Error getting location: ' + error.message + '</p>';
                    }
                );
            } else {
                document.getElementById('location-result').innerHTML = 
                    '<p>Geolocation not supported by your browser</p>';
            }
            </script>
            """
            
            st.components.v1.html(js_code, height=150)
            
            # Give user time to accept location permission
            time.sleep(2)
            
            # Now we'll use a separate JavaScript snippet to check if location was obtained
            check_js = """
            <script>
            // Function to check if location is stored
            function checkLocation() {
                var lat = localStorage.getItem('user_lat');
                var lng = localStorage.getItem('user_lng');
                
                if (lat && lng) {
                    // Create form to submit data to Streamlit
                    var form = document.createElement('form');
                    form.method = 'GET';
                    form.action = window.location.pathname;
                    
                    // Add lat input
                    var latInput = document.createElement('input');
                    latInput.type = 'hidden';
                    latInput.name = 'lat';
                    latInput.value = lat;
                    form.appendChild(latInput);
                    
                    // Add lng input
                    var lngInput = document.createElement('input');
                    lngInput.type = 'hidden';
                    lngInput.name = 'lng';
                    lngInput.value = lng;
                    form.appendChild(lngInput);
                    
                    // Submit the form
                    document.body.appendChild(form);
                    form.submit();
                    
                    return true;
                }
                return false;
            }
            
            // Check immediately
            if (!checkLocation()) {
                // If location not ready, check again in 2 seconds
                setTimeout(checkLocation, 2000);
            }
            </script>
            """
            
            st.components.v1.html(check_js, height=0)
            
            st.info("If location was detected, coordinates will appear here. If not, please accept location permission in your browser.")

# Check for coordinates in URL parameters
params = st.query_params
if 'lat' in params and 'lng' in params:
    try:
        # Get the coordinates
        lat = float(params['lat'])
        lng = float(params['lng'])
        
        # Display the coordinates
        st.success("Location obtained successfully!")
        st.write(f"Latitude: {lat}")
        st.write(f"Longitude: {lng}")
        
        # Create DataFrame for download
        df = pd.DataFrame({
            'Latitude': [lat],
            'Longitude': [lng],
            'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        # Create download button
        create_csv_download_link(df)
        
        # Clear the parameters to avoid duplicate processing
        new_params = st.query_params.to_dict()
        if 'lat' in new_params: del new_params['lat']
        if 'lng' in new_params: del new_params['lng']
        st.query_params.update(**new_params)
        
    except ValueError:
        st.error("Invalid coordinates received")

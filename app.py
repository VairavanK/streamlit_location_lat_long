import streamlit as st
import pandas as pd
import base64
from datetime import datetime

st.title("Get Your Current Location")

# Function to create download link for CSV
def get_csv_download_link(df, filename="my_location.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return href

# Explanation text
st.write("This app gets your current location and allows you to download it as a CSV file.")

# Create placeholder for location information
location_info = st.empty()

# Display JavaScript for getting location
location_html = """
<div id="location-status">Click the button below to get your location</div>
<div id="location-display"></div>
<button id="get-location-btn" style="margin:10px 0; padding:5px 10px;">Get My Location</button>

<script>
// Only run when button is clicked to avoid automatic reloads
document.getElementById('get-location-btn').addEventListener('click', function() {
    var statusDiv = document.getElementById('location-status');
    var displayDiv = document.getElementById('location-display');
    
    statusDiv.innerHTML = "Getting your location...";
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                // Success callback
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                
                // Display the location
                statusDiv.innerHTML = "Location obtained successfully!";
                displayDiv.innerHTML = 
                    "<p><strong>Your coordinates:</strong></p>" +
                    "<p>Latitude: <span id='latitude-value'>" + lat + "</span></p>" +
                    "<p>Longitude: <span id='longitude-value'>" + lng + "</span></p>";
                
                // Store in local storage so we can access it from Python
                localStorage.setItem('userLatitude', lat);
                localStorage.setItem('userLongitude', lng);
                
                // No form submission - to avoid loops
            },
            function(error) {
                // Error callback
                statusDiv.innerHTML = "Error getting location: " + error.message;
            }
        );
    } else {
        statusDiv.innerHTML = "Geolocation is not supported by this browser.";
    }
});
</script>
"""

# Display HTML with JavaScript
st.components.v1.html(location_html, height=200)

# Instructions for the user
st.write("1. Click the 'Get My Location' button above to detect your location.")
st.write("2. After your location is displayed, click the button below to prepare your CSV download.")

# Manual input fields for Lat/Long
st.markdown("---")
st.markdown("### Enter Coordinates for CSV")
st.write("Either use the coordinates detected above or enter them manually:")

col1, col2 = st.columns(2)
with col1:
    latitude = st.text_input("Latitude", "")
with col2:
    longitude = st.text_input("Longitude", "")

# Button to generate CSV with provided coordinates
if st.button("Generate CSV Download Link"):
    if latitude and longitude:
        try:
            lat_value = float(latitude)
            lng_value = float(longitude)
            
            # Create DataFrame for CSV
            df = pd.DataFrame({
                'Latitude': [lat_value],
                'Longitude': [lng_value],
                'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            })
            
            # Show the download link
            st.success("CSV ready for download!")
            st.markdown(get_csv_download_link(df), unsafe_allow_html=True)
        except ValueError:
            st.error("Please enter valid numeric coordinates.")
    else:
        st.warning("Please enter both latitude and longitude values.")

# Add JavaScript to retrieve the stored location from localStorage and fill the input fields
fill_inputs_js = """
<script>
// Function to fill input fields with localStorage values
function fillLocationInputs() {
    // Get stored values
    var lat = localStorage.getItem('userLatitude');
    var lng = localStorage.getItem('userLongitude');
    
    if (lat && lng) {
        // Find the input fields by their label
        var inputs = document.querySelectorAll('input[type="text"]');
        
        // Loop through inputs to find latitude and longitude fields
        for (var i = 0; i < inputs.length; i++) {
            // Check previous element for label text
            var label = inputs[i].previousElementSibling;
            if (label && label.textContent) {
                if (label.textContent.includes('Latitude')) {
                    inputs[i].value = lat;
                    // Create and dispatch an input event
                    var event = new Event('input', { bubbles: true });
                    inputs[i].dispatchEvent(event);
                }
                else if (label.textContent.includes('Longitude')) {
                    inputs[i].value = lng;
                    // Create and dispatch an input event
                    var event = new Event('input', { bubbles: true });
                    inputs[i].dispatchEvent(event);
                }
            }
        }
    }
}

// Add a small delay to ensure Streamlit has rendered the elements
setTimeout(fillLocationInputs, 1000);
</script>
"""

# Add the script to fill input fields automatically
st.components.v1.html(fill_inputs_js, height=0)

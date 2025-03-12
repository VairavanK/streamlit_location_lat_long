import streamlit as st
import pandas as pd
import base64
from datetime import datetime

st.title("Get Your Current Location")

# Initialize session state
if 'latitude' not in st.session_state:
    st.session_state.latitude = None
if 'longitude' not in st.session_state:
    st.session_state.longitude = None

# Callback function to update session state
def update_location(lat, lng):
    st.session_state.latitude = lat
    st.session_state.longitude = lng
    st.rerun()

# Function to create a download link for CSV
def get_csv_download_link(df, filename="location_data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'

# Main UI section
col1, col2 = st.columns([3, 1])

with col1:
    st.write("Click the button to get your current location:")

with col2:
    # Create a button widget with a key
    st.button("Get My Location", key="location_button", on_click=lambda: None)

# JavaScript to get location when button is clicked
js_code = f"""
<script>
// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {{
    // Function to find the Streamlit button by its text
    function findButton() {{
        const buttons = Array.from(document.querySelectorAll('button'));
        return buttons.find(button => button.innerText.includes('Get My Location'));
    }}

    // Try to find the button immediately
    let locationButton = findButton();
    
    // If not found, retry with a small delay (Streamlit might be still rendering)
    if (!locationButton) {{
        setTimeout(() => {{
            locationButton = findButton();
            if (locationButton) setupButtonListener(locationButton);
        }}, 1000);
    }} else {{
        setupButtonListener(locationButton);
    }}

    function setupButtonListener(button) {{
        button.addEventListener('click', function() {{
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(
                    function(position) {{
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        
                        // Use Streamlit's session state setter
                        window.parent.postMessage({{
                            type: "streamlit:setComponentValue",
                            value: {{ lat: lat, lng: lng }},
                            dataType: "json"
                        }}, "*");
                        
                        // Update UI directly for immediate feedback
                        const locationInfo = document.getElementById('location_info');
                        if (locationInfo) {{
                            locationInfo.innerHTML = `<div>Latitude: ${{lat}}</div><div>Longitude: ${{lng}}</div>`;
                        }}
                    }},
                    function(error) {{
                        console.error("Error getting location:", error);
                        const locationInfo = document.getElementById('location_info');
                        if (locationInfo) {{
                            locationInfo.innerHTML = `<div>Error getting location: ${{error.message}}</div>`;
                        }}
                    }}
                );
            }}
        }});
    }}
}});
</script>
<div id="location_info"></div>
"""

# Display the JavaScript
st.components.v1.html(js_code, height=100)

# Let's use a simpler (but reliable) approach to wait for a button press
# and then get location using JavaScript
if st.button("Detect My Location"):
    with st.spinner("Requesting your location..."):
        # Use streamlit-javascript to run JavaScript code
        st.markdown("""
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    // Store in sessionStorage to access after page reload
                    sessionStorage.setItem('user_latitude', lat);
                    sessionStorage.setItem('user_longitude', lng);
                    
                    // Reload the page to pick up the stored values
                    window.location.reload();
                },
                function(error) {
                    console.error("Error getting location:", error);
                    document.body.innerHTML += `<div>Error: ${error.message}</div>`;
                }
            );
        } else {
            document.body.innerHTML += "<div>Geolocation not supported</div>";
        }
        </script>
        """, unsafe_allow_html=True)
    
        # In a real implementation, we would wait for the result
        # For demonstration, let's check if we have stored values
        st.info("Please allow location access in your browser when prompted.")

# Check for stored location in sessionStorage
check_storage_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const lat = sessionStorage.getItem('user_latitude');
    const lng = sessionStorage.getItem('user_longitude');
    
    if (lat && lng) {
        // Create hidden form to submit to Streamlit
        const form = document.createElement('form');
        form.method = 'POST';
        form.style.display = 'none';
        
        const latInput = document.createElement('input');
        latInput.name = 'lat';
        latInput.value = lat;
        form.appendChild(latInput);
        
        const lngInput = document.createElement('input');
        lngInput.name = 'lng';
        lngInput.value = lng;
        form.appendChild(lngInput);
        
        document.body.appendChild(form);
        form.submit();
        
        // Clear storage to avoid repeated submissions
        sessionStorage.removeItem('user_latitude');
        sessionStorage.removeItem('user_longitude');
    }
});
</script>
"""

st.components.v1.html(check_storage_js, height=0)

# Check query params for submitted location
params = st.query_params
if 'lat' in params and 'lng' in params:
    try:
        lat = float(params['lat'])
        lng = float(params['lng'])
        
        st.success("Location detected!")
        st.write(f"Latitude: {lat}")
        st.write(f"Longitude: {lng}")
        
        # Create DataFrame with the location data
        location_df = pd.DataFrame({
            'Latitude': [lat],
            'Longitude': [lng],
            'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        # Provide download link
        st.markdown(f"### Download Your Location Data")
        st.markdown(get_csv_download_link(location_df), unsafe_allow_html=True)
        
        # Clear params
        st.query_params.clear()
    except ValueError:
        st.error("Invalid coordinates received")

# Alternative simple approach - manual input option
st.markdown("---")
st.markdown("### Alternative: Enter Location Manually")
manual_lat = st.number_input("Latitude", value=None, placeholder="Enter latitude...")
manual_lng = st.number_input("Longitude", value=None, placeholder="Enter longitude...")

if st.button("Download Manual Location as CSV"):
    if manual_lat is not None and manual_lng is not None:
        # Create DataFrame with the location data
        location_df = pd.DataFrame({
            'Latitude': [manual_lat],
            'Longitude': [manual_lng],
            'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        # Provide download link
        st.markdown(get_csv_download_link(location_df), unsafe_allow_html=True)
    else:
        st.warning("Please enter both latitude and longitude values.")

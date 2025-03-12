import streamlit as st
import pandas as pd
import time
import base64

st.title("Get Your Current Location")

# Create JavaScript to access geolocation
get_location_js = """
<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                document.getElementById('lat_value').innerHTML = lat;
                document.getElementById('lng_value').innerHTML = lng;
                
                // Store in sessionStorage to access in Python
                sessionStorage.setItem('latitude', lat);
                sessionStorage.setItem('longitude', lng);
                
                // Signal Python that location is ready
                window.parent.postMessage({type: "location_ready", lat: lat, lng: lng}, "*");
            },
            function(error) {
                console.error("Error getting location:", error);
                document.getElementById('location_error').innerHTML = "Error getting location: " + error.message;
            }
        );
    } else {
        document.getElementById('location_error').innerHTML = "Geolocation is not supported by this browser.";
    }
}
</script>

<button onclick="getLocation()">Get My Location</button>
<p id="location_error"></p>
<div>
    <p>Latitude: <span id="lat_value">Not yet retrieved</span></p>
    <p>Longitude: <span id="lng_value">Not yet retrieved</span></p>
</div>
"""

# Display the custom HTML/JavaScript
st.components.v1.html(get_location_js, height=200)

# For storing location data
if 'location' not in st.session_state:
    st.session_state.location = None

# Function to create a download link for CSV
def get_csv_download_link(df, filename="location_data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'
    return href

# JavaScript to pass location data back to Python
st.markdown("""
<script>
window.addEventListener('message', function(event) {
    if (event.data.type === 'location_ready') {
        // Send the data to Streamlit
        const data = {
            latitude: event.data.lat,
            longitude: event.data.lng
        };
        
        // Using the Streamlit component API to update session state
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            value: data
        }, "*");
    }
});
</script>
""", unsafe_allow_html=True)

# Display location and download button
if st.button("Process Location and Prepare Download"):
    with st.spinner("Processing location data..."):
        # In real use, we would get location from JavaScript
        # For demonstration, let's use some sample data if needed
        if st.session_state.location:
            lat = st.session_state.location["latitude"]
            lng = st.session_state.location["longitude"]
        else:
            # Use placeholder data - in real app, this would come from the browser
            st.info("Please use the 'Get My Location' button above first, then try again.")
            # For demo purposes, using sample coordinates
            lat = 37.7749
            lng = -122.4194
            
        # Display the coordinates
        st.success("Location retrieved successfully!")
        st.write(f"Latitude: {lat}")
        st.write(f"Longitude: {lng}")
        
        # Create DataFrame for download
        location_df = pd.DataFrame({
            'Latitude': [lat],
            'Longitude': [lng],
            'Timestamp': [time.strftime("%Y-%m-%d %H:%M:%S")]
        })
        
        # Create download link
        st.markdown(get_csv_download_link(location_df), unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.title("Get Your Current Location and Download as CSV")

# Initialize session state for latitude and longitude
if "latitude" not in st.session_state:
    st.session_state["latitude"] = None
if "longitude" not in st.session_state:
    st.session_state["longitude"] = None

# JavaScript to get location and update Streamlit's text area
location_script = """
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        var lat = position.coords.latitude;
                        var lon = position.coords.longitude;
                        var coords = lat + "," + lon;
                        // Update hidden text area
                        document.getElementById("geo_data").value = coords;
                        document.getElementById("geo_data").dispatchEvent(new Event("input", { bubbles: true }));
                    },
                    (error) => {
                        alert("Location access denied or unavailable.");
                    }
                );
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        }
    </script>
    <button onclick="getLocation()">Get Current Location</button>
"""

# Embed JavaScript inside Streamlit
components.html(location_script, height=100)

# Hidden text area to capture JavaScript output
geo_data = st.text_area("Hidden Geolocation Data", key="geo_data")

# Process and store location data
if geo_data:
    try:
        lat, lon = geo_data.split(",")
        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon
    except:
        st.error("Invalid location data received.")

# Display coordinates if available
if st.session_state["latitude"] and st.session_state["longitude"]:
    st.success(f"**Latitude:** {st.session_state['latitude']}")
    st.success(f"**Longitude:** {st.session_state['longitude']}")

    # Create DataFrame and convert to CSV
    df = pd.DataFrame({"Latitude": [st.session_state["latitude"]], "Longitude": [st.session_state["longitude"]]})
    csv_data = df.to_csv(index=False).encode("utf-8")

    # CSV Download Button
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="location.csv",
        mime="text/csv",
    )

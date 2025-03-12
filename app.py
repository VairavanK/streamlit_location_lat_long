import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.title("Get Your Current Location and Download as CSV")

# Initialize session state variables
if "latitude" not in st.session_state:
    st.session_state["latitude"] = None
if "longitude" not in st.session_state:
    st.session_state["longitude"] = None

# JavaScript to fetch user's location and update Streamlit session state
location_script = """
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        var lat = position.coords.latitude;
                        var lon = position.coords.longitude;
                        // Send data to Streamlit
                        var streamlit_data = lat + "," + lon;
                        var url = window.location.href.split('?')[0] + "?location=" + streamlit_data;
                        window.location.href = url;
                    },
                    (error) => {
                        document.body.innerHTML += "<p>Location access denied.</p>";
                    }
                );
            } else {
                document.body.innerHTML += "<p>Geolocation is not supported by this browser.</p>";
            }
        }
    </script>
    <button onclick="getLocation()">Get Current Location</button>
"""

# Render JavaScript inside Streamlit
components.html(location_script, height=100)

# Read URL parameters for location
query_params = st.query_params
if "location" in query_params:
    try:
        lat, lon = query_params["location"].split(",")
        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon
    except:
        st.error("Invalid location data received.")

# Display coordinates if available
if st.session_state["latitude"] and st.session_state["longitude"]:
    st.write(f"**Latitude:** {st.session_state['latitude']}")
    st.write(f"**Longitude:** {st.session_state['longitude']}")

    # Create a DataFrame for CSV export
    df = pd.DataFrame({"Latitude": [st.session_state["latitude"]], "Longitude": [st.session_state["longitude"]]})
    csv_data = df.to_csv(index=False).encode("utf-8")

    # CSV Download Button
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="location.csv",
        mime="text/csv",
    )

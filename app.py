import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.title("Get Your Current Location and Download as CSV")

# Initialize session state for latitude and longitude
if "latitude" not in st.session_state:
    st.session_state["latitude"] = None
if "longitude" not in st.session_state:
    st.session_state["longitude"] = None

# JavaScript to get user's geolocation and pass it to Streamlit
location_script = """
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        var lat = position.coords.latitude;
                        var lon = position.coords.longitude;

                        // Send the data back to Streamlit using an iframe trick
                        var streamlit_data = lat + "," + lon;
                        var iframe = document.createElement("iframe");
                        iframe.src = "https://localhost/?data=" + encodeURIComponent(streamlit_data);
                        iframe.style.display = "none";
                        document.body.appendChild(iframe);
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

# Render JavaScript inside Streamlit
components.html(location_script, height=100)

# Input field to receive location data from the frontend
location_input = st.text_input("Location Data (Hidden)", "")

# Process and store location data
if location_input:
    try:
        lat, lon = location_input.split(",")
        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon
    except:
        st.error("Invalid location data received.")

# Display location if available
if st.session_state["latitude"] and st.session_state["longitude"]:
    st.write(f"**Latitude:** {st.session_state['latitude']}")
    st.write(f"**Longitude:** {st.session_state['longitude']}")

    # Create DataFrame for CSV
    df = pd.DataFrame({"Latitude": [st.session_state["latitude"]], "Longitude": [st.session_state["longitude"]]})
    csv_data = df.to_csv(index=False).encode("utf-8")

    # Download button for CSV
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="location.csv",
        mime="text/csv",
    )

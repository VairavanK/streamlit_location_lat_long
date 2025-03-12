import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.title("Get Your Current Location and Download as CSV")

# Initialize session state variables to prevent reruns
if "latitude" not in st.session_state:
    st.session_state["latitude"] = None
if "longitude" not in st.session_state:
    st.session_state["longitude"] = None

# JavaScript to get user's geolocation and send it to Streamlit
location_script = """
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        var lat = position.coords.latitude;
                        var lon = position.coords.longitude;
                        
                        // Send the data back to Streamlit via an iframe
                        var iframe = document.createElement("iframe");
                        iframe.style.display = "none";
                        iframe.src = "https://yourserver.com?location=" + encodeURIComponent(lat + ',' + lon);
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

# Input field to receive location data (works as a bridge between JavaScript & Streamlit)
geo_data = st.text_input("Location Data", "")

# Process and store location data in session state
if geo_data and "," in geo_data:
    try:
        lat, lon = geo_data.split(",")
        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon
    except:
        st.error("Invalid location data received.")

# Display the retrieved coordinates
if st.session_state["latitude"] and st.session_state["longitude"]:
    st.success(f"Latitude: {st.session_state['latitude']}")
    st.success(f"Longitude: {st.session_state['longitude']}")

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

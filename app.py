import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.title("Get Your Current Location and Download as CSV")

# Initialize session state for latitude and longitude
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

                        // Send data back to Streamlit using a temporary input element
                        var streamlit_input = document.createElement("input");
                        streamlit_input.type = "hidden";
                        streamlit_input.name = "geo_data";
                        streamlit_input.value = lat + "," + lon;
                        document.body.appendChild(streamlit_input);

                        // Simulate form submission to trigger Streamlit update
                        var form = document.createElement("form");
                        form.method = "POST";
                        form.appendChild(streamlit_input);
                        document.body.appendChild(form);
                        form.submit();
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

# Embed JavaScript in Streamlit
components.html(location_script, height=100)

# Capture user input sent from JavaScript
geo_data = st.text_input("Hidden Geo Data", key="geo_data")

if geo_data:
    try:
        lat, lon = geo_data.split(",")
        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon
    except:
        st.error("Invalid location data received.")

# Display latitude and longitude
if st.session_state["latitude"] and st.session_state["longitude"]:
    st.write(f"**Latitude:** {st.session_state['latitude']}")
    st.write(f"**Longitude:** {st.session_state['longitude']}")

    # Create DataFrame for CSV export
    df = pd.DataFrame({"Latitude": [st.session_state["latitude"]], "Longitude": [st.session_state["longitude"]]})
    csv_data = df.to_csv(index=False).encode("utf-8")

    # Download button for CSV
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="location.csv",
        mime="text/csv",
    )

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.title("Get Your Current Location and Download as CSV")

# Initialize session state variables
if "latitude" not in st.session_state:
    st.session_state["latitude"] = None
if "longitude" not in st.session_state:
    st.session_state["longitude"] = None
if "location_fetched" not in st.session_state:
    st.session_state["location_fetched"] = False

# JavaScript to get geolocation **only when the button is clicked**
location_script = """
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        var lat = position.coords.latitude;
                        var lon = position.coords.longitude;
                        // Send data back to Streamlit
                        document.getElementById("geo_data").value = lat + "," + lon;
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
"""

# Show button to trigger JavaScript
st.write(location_script, unsafe_allow_html=True)
if st.button("Get Current Location"):
    components.html('<script>getLocation();</script>', height=0)

# Hidden text area to receive geolocation data from JavaScript
geo_data = st.text_input("Hidden Geolocation Data", key="geo_data")

# Process and store location data when received
if geo_data and not st.session_state["location_fetched"]:
    try:
        lat, lon = geo_data.split(",")
        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon
        st.session_state["location_fetched"] = True  # Prevent re-fetching
    except:
        st.error("Invalid location data received.")

# Display coordinates if available
if st.session_state["latitude"] and st.session_state["longitude"]:
    st.success(f"Latitude: {st.session_state['latitude']}")
    st.success(f"Longitude: {st.session_state['longitude']}")

    # Create DataFrame for CSV export
    df = pd.DataFrame({"Latitude": [st.session_state["latitude"]], "Longitude": [st.session_state["longitude"]]})
    csv_data = df.to_csv(index=False).encode("utf-8")

    # CSV Download Button
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="location.csv",
        mime="text/csv",
    )

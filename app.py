import streamlit as st
import pandas as pd
from streamlit_javascript import st_javascript

st.title("Get Your Current Location and Download as CSV")

# JavaScript to get geolocation
location = st_javascript(
    """
    async function getLocation() {
        return new Promise((resolve) => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        resolve({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        });
                    },
                    (error) => {
                        resolve({ error: "Location access denied" });
                    }
                );
            } else {
                resolve({ error: "Geolocation not supported" });
            }
        });
    }
    getLocation();
    """
)

if location and "latitude" in location and "longitude" in location:
    lat = location["latitude"]
    lon = location["longitude"]

    st.write(f"**Latitude:** {lat}")
    st.write(f"**Longitude:** {lon}")

    # Create a DataFrame and convert it to CSV
    df = pd.DataFrame({"Latitude": [lat], "Longitude": [lon]})
    csv_data = df.to_csv(index=False).encode("utf-8")

    # Provide a download button for the CSV file
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="location.csv",
        mime="text/csv",
    )
elif location and "error" in location:
    st.error(location["error"])

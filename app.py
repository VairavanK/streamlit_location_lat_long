import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.title("Get Your Current Location and Download as CSV")

# Read URL query parameters for latitude and longitude
query_params = st.experimental_get_query_params()
lat = query_params.get("lat", [None])[0]
lon = query_params.get("lon", [None])[0]

if lat and lon:
    st.write("Your Coordinates:")
    st.write("Latitude:", lat)
    st.write("Longitude:", lon)
    
    # Create a DataFrame with the coordinates
    df = pd.DataFrame({"Latitude": [lat], "Longitude": [lon]})
    csv_data = df.to_csv(index=False).encode('utf-8')
    
    # Provide a download button for the CSV file
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name='location.csv',
        mime='text/csv',
    )
else:
    if st.button("Get Current Location"):
        # The JavaScript gets the user's location and reloads the page with query parameters
        components.html(
            """
            <html>
              <body>
                <script>
                  if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function(position) {
                      var lat = position.coords.latitude;
                      var lon = position.coords.longitude;
                      // Construct a new URL with the latitude and longitude as query parameters
                      var newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname + "?lat=" + lat + "&lon=" + lon;
                      window.location.href = newUrl;
                    }, function(error) {
                      document.body.innerHTML = "<p>Unable to retrieve your location.</p>";
                    });
                  } else {
                    document.body.innerHTML = "<p>Geolocation is not supported by this browser.</p>";
                  }
                </script>
              </body>
            </html>
            """,
            height=200,
        )

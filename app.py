import streamlit as st
import streamlit.components.v1 as components

st.title("Get Your Current Location")

if st.button("Get Current Location"):
    # This HTML/JavaScript snippet gets the user's location and writes it to the page.
    components.html(
        """
        <html>
          <body>
            <script>
              // Check if the geolocation API is available
              if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                  var lat = position.coords.latitude;
                  var lon = position.coords.longitude;
                  document.body.innerHTML = "<h3>Your Coordinates</h3>" +
                    "<p>Latitude: " + lat + "</p>" +
                    "<p>Longitude: " + lon + "</p>";
                }, function(error) {
                  document.body.innerHTML = "<p>Unable to retrieve your location</p>";
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

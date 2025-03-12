import streamlit as st
 import pandas as pd
 import base64
 import time
 from datetime import datetime
 
 st.title("Get Your Current Location")
 st.title("Get My Current Location")
 
 # Function to create download link for CSV
 def get_csv_download_link(df, filename="my_location.csv"):
 # Function to create a downloadable CSV
 def create_csv_download_link(df):
     csv = df.to_csv(index=False)
     b64 = base64.b64encode(csv.encode()).decode()
     href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
     return href
     # Use Streamlit's built-in download button
     st.download_button(
         label="Download CSV",
         data=csv,
         file_name="my_location.csv",
         mime="text/csv"
     )
 
 # Explanation text
 st.write("This app gets your current location and allows you to download it as a CSV file.")
 # Container for location result
 location_display = st.container()
 
 # Create placeholder for location information
 location_info = st.empty()
 
 # Display JavaScript for getting location
 location_html = """
 <div id="location-status">Click the button below to get your location</div>
 <div id="location-display"></div>
 <button id="get-location-btn" style="margin:10px 0; padding:5px 10px;">Get My Location</button>
 
 <script>
 // Only run when button is clicked to avoid automatic reloads
 document.getElementById('get-location-btn').addEventListener('click', function() {
     var statusDiv = document.getElementById('location-status');
     var displayDiv = document.getElementById('location-display');
     
     statusDiv.innerHTML = "Getting your location...";
     
     if (navigator.geolocation) {
         navigator.geolocation.getCurrentPosition(
             function(position) {
                 // Success callback
                 var lat = position.coords.latitude;
                 var lng = position.coords.longitude;
                 
                 // Display the location
                 statusDiv.innerHTML = "Location obtained successfully!";
                 displayDiv.innerHTML = 
                     "<p><strong>Your coordinates:</strong></p>" +
                     "<p>Latitude: <span id='latitude-value'>" + lat + "</span></p>" +
                     "<p>Longitude: <span id='longitude-value'>" + lng + "</span></p>";
                 
                 // Store in local storage so we can access it from Python
                 localStorage.setItem('userLatitude', lat);
                 localStorage.setItem('userLongitude', lng);
                 
                 // No form submission - to avoid loops
             },
             function(error) {
                 // Error callback
                 statusDiv.innerHTML = "Error getting location: " + error.message;
 if st.button("Get My Location"):
     # Simple container to display coordinates
     with location_display:
         with st.spinner("Getting your location..."):
             # Insert JavaScript to get the location
             js_code = """
             <div id="location-result">Detecting location...</div>
             
             <script>
             if (navigator.geolocation) {
                 navigator.geolocation.getCurrentPosition(
                     function(position) {
                         // Success
                         document.getElementById('location-result').innerHTML = 
                             '<p>Location found:</p>' +
                             '<p>Latitude: <span id="lat">' + position.coords.latitude + '</span></p>' +
                             '<p>Longitude: <span id="lng">' + position.coords.longitude + '</span></p>';
                             
                         // Store in localStorage for streamlit to access
                         localStorage.setItem('user_lat', position.coords.latitude);
                         localStorage.setItem('user_lng', position.coords.longitude);
                         
                         // Signal that location is ready by changing URL hash
                         window.location.hash = 'location-ready';
                     },
                     function(error) {
                         // Error
                         document.getElementById('location-result').innerHTML = 
                             '<p>Error getting location: ' + error.message + '</p>';
                     }
                 );
             } else {
                 document.getElementById('location-result').innerHTML = 
                     '<p>Geolocation not supported by your browser</p>';
             }
         );
     } else {
         statusDiv.innerHTML = "Geolocation is not supported by this browser.";
     }
 });
 </script>
 """
 
 # Display HTML with JavaScript
 st.components.v1.html(location_html, height=200)
 
 # Instructions for the user
 st.write("1. Click the 'Get My Location' button above to detect your location.")
 st.write("2. After your location is displayed, click the button below to prepare your CSV download.")
 
 # Manual input fields for Lat/Long
 st.markdown("---")
 st.markdown("### Enter Coordinates for CSV")
 st.write("Either use the coordinates detected above or enter them manually:")
 
 col1, col2 = st.columns(2)
 with col1:
     latitude = st.text_input("Latitude", "")
 with col2:
     longitude = st.text_input("Longitude", "")
 
 # Button to generate CSV with provided coordinates
 if st.button("Generate CSV Download Link"):
     if latitude and longitude:
         try:
             lat_value = float(latitude)
             lng_value = float(longitude)
             </script>
             """
 
             # Create DataFrame for CSV
             df = pd.DataFrame({
                 'Latitude': [lat_value],
                 'Longitude': [lng_value],
                 'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
             })
             st.components.v1.html(js_code, height=150)
 
             # Show the download link
             st.success("CSV ready for download!")
             st.markdown(get_csv_download_link(df), unsafe_allow_html=True)
         except ValueError:
             st.error("Please enter valid numeric coordinates.")
     else:
         st.warning("Please enter both latitude and longitude values.")
 
 # Add JavaScript to retrieve the stored location from localStorage and fill the input fields
 fill_inputs_js = """
 <script>
 // Function to fill input fields with localStorage values
 function fillLocationInputs() {
     // Get stored values
     var lat = localStorage.getItem('userLatitude');
     var lng = localStorage.getItem('userLongitude');
     
     if (lat && lng) {
         // Find the input fields by their label
         var inputs = document.querySelectorAll('input[type="text"]');
         
         // Loop through inputs to find latitude and longitude fields
         for (var i = 0; i < inputs.length; i++) {
             // Check previous element for label text
             var label = inputs[i].previousElementSibling;
             if (label && label.textContent) {
                 if (label.textContent.includes('Latitude')) {
                     inputs[i].value = lat;
                     // Create and dispatch an input event
                     var event = new Event('input', { bubbles: true });
                     inputs[i].dispatchEvent(event);
                 }
                 else if (label.textContent.includes('Longitude')) {
                     inputs[i].value = lng;
                     // Create and dispatch an input event
                     var event = new Event('input', { bubbles: true });
                     inputs[i].dispatchEvent(event);
             # Give user time to accept location permission
             time.sleep(2)
             
             # Now we'll use a separate JavaScript snippet to check if location was obtained
             check_js = """
             <script>
             // Function to check if location is stored
             function checkLocation() {
                 var lat = localStorage.getItem('user_lat');
                 var lng = localStorage.getItem('user_lng');
                 
                 if (lat && lng) {
                     // Create form to submit data to Streamlit
                     var form = document.createElement('form');
                     form.method = 'GET';
                     form.action = window.location.pathname;
                     
                     // Add lat input
                     var latInput = document.createElement('input');
                     latInput.type = 'hidden';
                     latInput.name = 'lat';
                     latInput.value = lat;
                     form.appendChild(latInput);
                     
                     // Add lng input
                     var lngInput = document.createElement('input');
                     lngInput.type = 'hidden';
                     lngInput.name = 'lng';
                     lngInput.value = lng;
                     form.appendChild(lngInput);
                     
                     // Submit the form
                     document.body.appendChild(form);
                     form.submit();
                     
                     return true;
                 }
                 return false;
             }
         }
     }
 }
 
 // Add a small delay to ensure Streamlit has rendered the elements
 setTimeout(fillLocationInputs, 1000);
 </script>
 """
             
             // Check immediately
             if (!checkLocation()) {
                 // If location not ready, check again in 2 seconds
                 setTimeout(checkLocation, 2000);
             }
             </script>
             """
             
             st.components.v1.html(check_js, height=0)
             
             st.info("If location was detected, coordinates will appear here. If not, please accept location permission in your browser.")
 
 # Add the script to fill input fields automatically
 st.components.v1.html(fill_inputs_js, height=0)
 # Check for coordinates in URL parameters
 params = st.query_params
 if 'lat' in params and 'lng' in params:
     try:
         # Get the coordinates
         lat = float(params['lat'])
         lng = float(params['lng'])
         
         # Display the coordinates
         st.success("Location obtained successfully!")
         st.write(f"Latitude: {lat}")
         st.write(f"Longitude: {lng}")
         
         # Create DataFrame for download
         df = pd.DataFrame({
             'Latitude': [lat],
             'Longitude': [lng],
             'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
         })
         
         # Create download button
         create_csv_download_link(df)
         
         # Clear the parameters to avoid duplicate processing
         new_params = st.query_params.to_dict()
         if 'lat' in new_params: del new_params['lat']
         if 'lng' in new_params: del new_params['lng']
         st.query_params.update(**new_params)
         
     except ValueError:
         st.error("Invalid coordinates received")

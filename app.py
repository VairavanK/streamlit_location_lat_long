import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation, streamlit_js_eval

st.title("Simple Location App")

# Initialize session state
if 'location_requested' not in st.session_state:
    st.session_state.location_requested = False
if 'location_data' not in st.session_state:
    st.session_state.location_data = None

# Function to create CSV download
def create_csv_download(lat, lng):
    df = pd.DataFrame({
        'Latitude': [lat],
        'Longitude': [lng],
        'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="my_location.csv",
        mime="text/csv"
    )

# Information about location permissions
st.info("This app requires location permissions. Please allow when prompted by your browser.")

# Button to get location
if st.button("Get My Location") or st.session_state.location_requested:
    st.session_state.location_requested = True
    
    try:
        with st.spinner("Getting your location..."):
            # Use streamlit-js-eval to get location data
            location_data = get_geolocation()
            
            if location_data is None:
                # User may not have responded to permission prompt yet
                st.warning("Waiting for location permission... If no prompt appears, please check your browser settings.")
                
                # Insert some JavaScript to help users understand what's happening
                st.components.v1.html("""
                <script>
                // Check if geolocation is supported
                if (navigator.geolocation) {
                    document.write("<p>Please allow location access when prompted by your browser.</p>");
                    
                    // Test if permissions might be denied
                    navigator.permissions.query({name:'geolocation'}).then(function(result) {
                        if (result.state === 'denied') {
                            document.write("<p style='color:red;'>Location access appears to be blocked. Please check your browser settings and reload this page.</p>");
                        }
                    });
                } else {
                    document.write("<p style='color:red;'>Your browser doesn't support geolocation.</p>");
                }
                </script>
                """, height=100)
                
                # Add a manual refresh option
                if st.button("I've granted permission - refresh"):
                    st.rerun()
            else:
                # Store in session state
                st.session_state.location_data = location_data
    except Exception as e:
        st.error(f"Error: {e}")
        st.markdown("If you're having trouble, try refreshing the page or check if location is enabled in your browser.")

# Process and display location if we have it
if st.session_state.location_data and 'coords' in st.session_state.location_data:
    coords = st.session_state.location_data['coords']
    latitude = coords['latitude']
    longitude = coords['longitude']
    
    st.success("Location obtained successfully!")
    
    # Display coordinates in a nice format
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Latitude", f"{latitude:.6f}")
    with col2:
        st.metric("Longitude", f"{longitude:.6f}")
    
    # Create map showing the location
    try:
        import folium
        from streamlit_folium import folium_static
        
        st.write("Your location on map:")
        m = folium.Map(location=[latitude, longitude], zoom_start=13)
        folium.Marker([latitude, longitude], popup="Your Location").add_to(m)
        folium_static(m)
    except ImportError:
        st.write("Map display not available (requires folium package)")
    
    # Create download button
    st.subheader("Download Your Location Data")
    create_csv_download(latitude, longitude)
    
    # Reset button
    if st.button("Reset"):
        st.session_state.location_requested = False
        st.session_state.location_data = None
        st.rerun()

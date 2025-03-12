import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from io import BytesIO
import uuid
from PIL import Image
from streamlit_js_eval import get_geolocation
from streamlit_back_camera_input import back_camera_input

# Set page config
st.set_page_config(page_title="Data Enrichment App", layout="wide")

# Add custom component fixes and performance optimization for geolocation
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    /* Mobile-friendly styling */
    @media (max-width: 768px) {
        .stButton button {
            width: 100%;
            padding: 15px 0;
            margin-bottom: 10px;
        }
        
        /* Make the app full width on mobile */
        .main .block-container {
            padding-left: 5px;
            padding-right: 5px;
            max-width: 100%;
        }
        
        /* Make expanders more touch-friendly */
        .streamlit-expanderHeader {
            font-size: 1.2rem;
            padding: 12px 0;
        }
    }
    
    /* Enhanced download button */
    .big-camera-button {
        display: block;
        width: 100%;
        padding: 15px;
        background-color: #1E88E5;
        color: white;
        text-align: center;
        font-size: 16px;
        margin-top: 10px;
        border-radius: 5px;
        cursor: pointer;
        text-decoration: none;
    }

    /* Standard button styling */
    .stButton > button {
        font-weight: bold;
    }
    
    /* Improved camera prompt */
    .camera-prompt {
        background-color: rgba(0,0,0,0.7);
        color: white;
        text-align: center;
        padding: 8px 16px;
        font-size: 16px;
        border-radius: 20px;
        margin: 10px auto;
        width: fit-content;
    }
    
    /* Give more room for the camera component */
    [data-testid="stVerticalBlock"] iframe {
        min-height: 360px !important;
    }
    
    /* Preview image styling */
    .preview-image {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 5px;
        background-color: #f8f9fa;
    }
</style>

<script>
// Custom script to ensure camera component frame is visible
document.addEventListener('DOMContentLoaded', function() {
    // Set interval to periodically check for iframes and ensure they have enough height
    setInterval(function() {
        const iframes = document.querySelectorAll('iframe');
        iframes.forEach(function(iframe) {
            if (iframe.height < 300) {
                iframe.height = 360;
                iframe.style.minHeight = '360px';
            }
        });
    }, 1000);
    
    // Optimize geolocation by cleaning up previous watchers
    window.streamlitGeoWatchId = null;
});
</script>
""", unsafe_allow_html=True)

# Session state initialization
if 'data' not in st.session_state:
    st.session_state.data = None
if 'selected_column' not in st.session_state:
    st.session_state.selected_column = None
if 'progress' not in st.session_state:
    st.session_state.progress = {}
if 'location_column' not in st.session_state:
    st.session_state.location_column = None
if 'image_column' not in st.session_state:
    st.session_state.image_column = None
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = {}
if 'search_term' not in st.session_state:
    st.session_state.search_term = ""
if 'active_capture_value' not in st.session_state:
    st.session_state.active_capture_value = None
if 'location_requested' not in st.session_state:
    st.session_state.location_requested = {}
if 'temp_photo' not in st.session_state:
    st.session_state.temp_photo = None

# Function to compress and encode image to base64
def compress_and_encode_image(image_data, max_size=(800, 800), quality=75):
    try:
        # Open the image
        img = Image.open(BytesIO(image_data))
        
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = rgb_img
        
        # Resize if larger than max_size
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)
        
        # Save to BytesIO with compression
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality)
        output.seek(0)
        
        # Encode to base64
        encoded = base64.b64encode(output.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        st.error(f"Error compressing image: {e}")
        return None

# Function to generate a download link for the CSV
def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"enriched_data_{timestamp}.csv"
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="big-camera-button">Download Enriched CSV</a>'
    return href

# Save location data
def save_location(value, lat, lng):
    if st.session_state.location_column is None:
        st.session_state.location_column = f"{st.session_state.selected_column}_location"
        if st.session_state.location_column not in st.session_state.data.columns:
            st.session_state.data[st.session_state.location_column] = None
    
    # Find the row index for the value
    row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column].astype(str) == str(value)].index
    if not row_idx.empty:
        st.session_state.data.loc[row_idx, st.session_state.location_column] = f"{lat}, {lng}"
        st.session_state.progress[value]['location'] = True
        return True
    return False

# Save image data as base64 encoded string
def save_image(value, image_data):
    if st.session_state.image_column is None:
        st.session_state.image_column = f"{st.session_state.selected_column}_image"
        if st.session_state.image_column not in st.session_state.data.columns:
            st.session_state.data[st.session_state.image_column] = None
    
    try:
        # Compress and encode the image
        base64_image = compress_and_encode_image(image_data)
        
        if base64_image:
            # Find the row index for the value
            row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column].astype(str) == str(value)].index
            if not row_idx.empty:
                # Store base64 image directly in the dataframe
                st.session_state.data.loc[row_idx, st.session_state.image_column] = base64_image
                st.session_state.progress[value]['image'] = True
                return True
        else:
            st.error("Failed to process image")
    except Exception as e:
        st.error(f"Error saving image: {e}")
    return False

# Display image from base64
def display_image_from_base64(base64_string, width=200):
    if base64_string and isinstance(base64_string, str) and base64_string.startswith('data:image'):
        st.markdown(f'<img src="{base64_string}" width="{width}" style="border-radius: 5px;">', unsafe_allow_html=True)
    else:
        st.write("No image available")

# Filter values based on search term
def filter_values(values, search_term):
    if not search_term:
        return values
    search_term = str(search_term).lower()
    return [v for v in values if search_term in str(v).lower()]

# Optimized geolocation function that uses a custom component to prevent memory leaks
def get_location_optimized():
    # Create a custom component with JS code that properly handles geolocation and cleanup
    loc_html = """
    <div id="location-container">Getting location...</div>
    
    <script>
    // Function to clean up previous watchers
    function cleanupGeoWatchers() {
        if (window.streamlitGeoWatchId !== null && 
            typeof window.streamlitGeoWatchId !== 'undefined') {
            navigator.geolocation.clearWatch(window.streamlitGeoWatchId);
            window.streamlitGeoWatchId = null;
            console.log("Cleared previous geolocation watcher");
        }
    }
    
    // Clean up before starting a new one
    cleanupGeoWatchers();
    
    // Function to send data back to Streamlit
    function sendToStreamlit(data) {
        const stringData = JSON.stringify(data);
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: stringData
        }, '*');
    }
    
    // Handle errors
    function handleError(error) {
        console.error("Geolocation error:", error);
        let errorMessage = "Error getting location: ";
        
        switch(error.code) {
            case error.PERMISSION_DENIED:
                errorMessage += "Permission denied. Please allow location access.";
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage += "Position unavailable.";
                break;
            case error.TIMEOUT:
                errorMessage += "Request timed out.";
                break;
            default:
                errorMessage += "Unknown error.";
                break;
        }
        
        document.getElementById('location-container').textContent = errorMessage;
        sendToStreamlit({error: errorMessage});
        
        // Cleanup after error
        cleanupGeoWatchers();
    }
    
    // Handle success
    function handleSuccess(position) {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        
        document.getElementById('location-container').textContent = 
            `Location found: ${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        
        sendToStreamlit({
            latitude: lat,
            longitude: lng
        });
        
        // Cleanup after success
        cleanupGeoWatchers();
    }
    
    // Get current position with optimized options
    const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    };
    
    try {
        if (navigator.geolocation) {
            // Use getCurrentPosition instead of watchPosition for one-time requests
            navigator.geolocation.getCurrentPosition(handleSuccess, handleError, options);
        } else {
            document.getElementById('location-container').textContent = 
                "Geolocation is not supported by this browser.";
            sendToStreamlit({error: "Geolocation not supported"});
        }
    } catch (e) {
        document.getElementById('location-container').textContent = 
            "Error initializing geolocation: " + e.message;
        sendToStreamlit({error: e.message});
    }
    </script>
    """
    
    # Return results from custom component
    result = st.components.v1.html(loc_html, height=50, key=f"geo_{uuid.uuid4()}")
    
    # Process the result
    if result:
        try:
            import json
            location_data = json.loads(result)
            
            if 'error' in location_data:
                st.error(location_data['error'])
                return None
            else:
                return location_data.get('latitude'), location_data.get('longitude')
        except Exception as e:
            st.error(f"Error processing location data: {e}")
            return None
    
    return None

# Get and save location with optimized performance
def get_and_save_location(value, prefix=""):
    # Make a unique location request key for this value and prefix
    loc_request_key = f"{prefix}_{value}"
    
    # If we haven't already requested location for this key
    if loc_request_key not in st.session_state.location_requested:
        st.session_state.location_requested[loc_request_key] = False
    
    # Button to get location OR continue if already requested
    if st.button(f"📍 Get Location", key=f"{prefix}_getloc_{value}") or st.session_state.location_requested[loc_request_key]:
        # Set flag that we've requested location
        st.session_state.location_requested[loc_request_key] = True
        
        with st.spinner("Getting your location..."):
            # Use our optimized location function
            location = get_location_optimized()
            
            if location:
                latitude, longitude = location
                if save_location(value, latitude, longitude):
                    st.success(f"Location saved: {latitude:.6f}, {longitude:.6f}")
                    # Reset flag
                    st.session_state.location_requested[loc_request_key] = False
                    return True
                else:
                    st.error("Failed to save location data")
                    st.session_state.location_requested[loc_request_key] = False
            else:
                st.warning("Waiting for location. If no prompt appears, please check your browser settings.")
                
                # Add cancel option
                if st.button("Cancel", key=f"{prefix}_cancel_loc_{value}"):
                    st.session_state.location_requested[loc_request_key] = False
                    st.rerun()
    
    return False

# Main app
def main():
    st.title("Data Enrichment with Location and Images")
    
    # Step 1: Upload CSV file
    if st.session_state.data is None:
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        
        if uploaded_file:
            try:
                st.session_state.data = pd.read_csv(uploaded_file)
                st.success("CSV file uploaded successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Step 2: Column selection
    if st.session_state.data is not None:
        if st.session_state.selected_column is None:
            st.write("Preview of your data:")
            st.dataframe(st.session_state.data.head())
            
            columns = list(st.session_state.data.columns)
            selected_column = st.selectbox("Select a column to enrich:", columns)
            
            if st.button("Confirm Column"):
                st.session_state.selected_column = selected_column
                
                # Initialize progress tracking for each value
                unique_values = st.session_state.data[st.session_state.selected_column].astype(str).unique()
                
                for value in unique_values:
                    if value not in st.session_state.progress:
                        st.session_state.progress[value] = {'location': False, 'image': False}
                    if value not in st.session_state.camera_active:
                        st.session_state.camera_active[value] = False
                
                st.rerun()
        
        # Step 3: Enrich each value
        if st.session_state.selected_column is not None:
            
            # Handle active image capture session
            if st.session_state.active_capture_value is not None:
                value = st.session_state.active_capture_value
                st.subheader(f"Taking Photo for: {value}")
                
                # Simple instructions before camera
                st.info("Position your item and tap directly on the camera view to capture")
                
                # Create two columns for camera and preview
                col1, col2 = st.columns(2)
                
                with col1:
                    # Camera column
                    st.markdown("### Camera")
                    # Add some space around the camera component
                    st.markdown('<div style="padding:5px 0;"></div>', unsafe_allow_html=True)
                    
                    # Use custom component directly with minimal parameters
                    photo = back_camera_input("", key=f"cam_{value}")
                    
                    # Add tap to capture text
                    st.markdown('<div class="camera-prompt">👆 Tap to capture</div>', unsafe_allow_html=True)
                    
                    # Cancel button
                    if st.button("❌ Cancel", key=f"cam_cancel_{value}"):
                        st.session_state.active_capture_value = None
                        st.session_state.temp_photo = None
                        st.rerun()
                
                with col2:
                    # Preview column
                    st.markdown("### Preview")
                    
                    # Process the captured image immediately for preview
                    if photo is not None:
                        try:
                            # Store the photo temporarily for preview
                            st.session_state.temp_photo = photo.getvalue()
                            
                            # Display preview - using use_container_width instead of use_column_width
                            img = Image.open(BytesIO(st.session_state.temp_photo))
                            st.image(img, use_container_width=True, caption="Current capture")
                            
                            # Add save button
                            if st.button("✅ Save & Continue", key="save_photo"):
                                if save_image(value, st.session_state.temp_photo):
                                    st.success("Photo saved successfully!")
                                    st.session_state.active_capture_value = None
                                    st.session_state.temp_photo = None
                                    st.rerun()
                                else:
                                    st.error("Failed to save photo. Please try again.")
                            
                            # Add retake button
                            if st.button("🔄 Retake", key="retake_photo"):
                                st.session_state.temp_photo = None
                                st.rerun()
                                
                        except Exception as e:
                            st.error(f"Error processing photo: {e}")
                    elif st.session_state.temp_photo is not None:
                        # Display previously captured photo - using use_container_width instead of use_column_width
                        img = Image.open(BytesIO(st.session_state.temp_photo))
                        st.image(img, use_container_width=True, caption="Current capture")
                        
                        # Add save button
                        if st.button("✅ Save & Continue", key="save_photo_existing"):
                            if save_image(value, st.session_state.temp_photo):
                                st.success("Photo saved successfully!")
                                st.session_state.active_capture_value = None
                                st.session_state.temp_photo = None
                                st.rerun()
                            else:
                                st.error("Failed to save photo. Please try again.")
                        
                        # Add retake button
                        if st.button("🔄 Retake", key="retake_photo_existing"):
                            st.session_state.temp_photo = None
                            st.rerun()
                    else:
                        st.write("No photo captured yet. Tap on the camera to take a picture.")
                
                # Early return if we're capturing an image
                return
                
            # Main enrichment UI
            st.write(f"Enriching data for column: **{st.session_state.selected_column}**")
            
            # Convert to strings to avoid numpy array issues
            unique_values = st.session_state.data[st.session_state.selected_column].astype(str).unique().tolist()
            
            # Search and filter functionality
            search_term = st.text_input("🔍 Search values:", value=st.session_state.search_term)
            if search_term != st.session_state.search_term:
                st.session_state.search_term = search_term
                st.rerun()
                
            # Filter values based on search
            filtered_values = filter_values(unique_values, st.session_state.search_term)
            
            if st.session_state.search_term and len(filtered_values) < len(unique_values):
                st.write(f"Showing {len(filtered_values)} of {len(unique_values)} values")
                
            # Display values to enrich
            st.write("## Values to enrich")
            
            # Create tabs for "In Progress" and "Completed"
            in_progress_tab, completed_tab, all_tab = st.tabs(["In Progress", "Completed", "All Values"])
            
            # Helper functions for grouping values
            def get_in_progress_values():
                return [v for v in filtered_values if not (
                    st.session_state.progress.get(v, {}).get('location', False) and 
                    st.session_state.progress.get(v, {}).get('image', False)
                )]
                
            def get_completed_values():
                return [v for v in filtered_values if (
                    st.session_state.progress.get(v, {}).get('location', False) and 
                    st.session_state.progress.get(v, {}).get('image', False)
                )]
            
            # In Progress Tab
            with in_progress_tab:
                in_progress_values = get_in_progress_values()
                if in_progress_values:
                    for value in in_progress_values:
                        with st.expander(f"{value}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                loc_status = "✅" if st.session_state.progress.get(value, {}).get('location', False) else "❌"
                                st.write(f"Location: {loc_status}")
                                
                                # Only show location button if location not captured yet
                                if not st.session_state.progress.get(value, {}).get('location', False):
                                    if get_and_save_location(value, prefix="ip"):
                                        st.rerun()
                            
                            with col2:
                                img_status = "✅" if st.session_state.progress.get(value, {}).get('image', False) else "❌"
                                st.write(f"Image: {img_status}")
                                
                                # Only show camera button if image not captured yet
                                if not st.session_state.progress.get(value, {}).get('image', False):
                                    if st.button(f"📸 Take Photo", key=f"ip_activate_{value}"):
                                        st.session_state.active_capture_value = value
                                        st.session_state.temp_photo = None
                                        st.rerun()
                else:
                    if st.session_state.search_term:
                        st.info(f"No in-progress values match your search: '{st.session_state.search_term}'")
                    else:
                        st.info("No values in progress - all are completed!")
                
            # Completed Tab
            with completed_tab:
                completed_values = get_completed_values()
                if completed_values:
                    for value in completed_values:
                        with st.expander(f"{value} ✅"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("Location: ✅")
                                row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column].astype(str) == value].index[0]
                                loc_col = st.session_state.location_column
                                if loc_col and loc_col in st.session_state.data.columns:
                                    loc_data = st.session_state.data.loc[row_idx, loc_col]
                                    st.write(f"Saved location: {loc_data}")
                            
                            with col2:
                                st.write("Image: ✅")
                                row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column].astype(str) == value].index[0]
                                img_col = st.session_state.image_column
                                if img_col and img_col in st.session_state.data.columns:
                                    base64_image = st.session_state.data.loc[row_idx, img_col]
                                    display_image_from_base64(base64_image)
                else:
                    if st.session_state.search_term:
                        st.info(f"No completed values match your search: '{st.session_state.search_term}'")
                    else:
                        st.info("No completed values yet!")
                
            # All Values Tab
            with all_tab:
                if len(filtered_values) > 0:
                    for value in filtered_values:
                        location_done = st.session_state.progress.get(value, {}).get('location', False)
                        image_done = st.session_state.progress.get(value, {}).get('image', False)
                        status = "✅" if location_done and image_done else "🔄"
                        
                        with st.expander(f"{value} {status}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                loc_status = "✅" if location_done else "❌"
                                st.write(f"Location: {loc_status}")
                                
                                if not location_done:
                                    # Use a different prefix for all_tab to create unique keys
                                    if get_and_save_location(value, prefix="all"):
                                        st.rerun()
                                else:
                                    row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column].astype(str) == value].index[0]
                                    loc_col = st.session_state.location_column
                                    if loc_col and loc_col in st.session_state.data.columns:
                                        loc_data = st.session_state.data.loc[row_idx, loc_col]
                                        st.write(f"Saved location: {loc_data}")
                            
                            with col2:
                                img_status = "✅" if image_done else "❌"
                                st.write(f"Image: {img_status}")
                                
                                if not image_done:
                                    if st.button(f"📸 Take Photo", key=f"all_activate_{value}"):
                                        st.session_state.active_capture_value = value
                                        st.session_state.temp_photo = None
                                        st.rerun()
                                else:
                                    row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column].astype(str) == value].index[0]
                                    img_col = st.session_state.image_column
                                    if img_col and img_col in st.session_state.data.columns:
                                        base64_image = st.session_state.data.loc[row_idx, img_col]
                                        display_image_from_base64(base64_image)
                else:
                    st.info(f"No values match your search: '{st.session_state.search_term}'")
            
            # Display progress stats
            total = len(unique_values)
            completed_count = len([v for v in unique_values if (
                st.session_state.progress.get(v, {}).get('location', False) and 
                st.session_state.progress.get(v, {}).get('image', False)
            )])
            
            progress_pct = int(completed_count/total*100) if total else 0
            st.write(f"## Progress: {completed_count}/{total} values completed ({progress_pct}%)")
            
            # Download section
            st.write("## Download Enriched Data")
            st.write("When you are finished, you can download the enriched data.")
            
            if st.button("Prepare Download"):
                st.markdown(get_csv_download_link(st.session_state.data), unsafe_allow_html=True)
                
            # Option to start over
            if st.button("Start Over (Clear Session)"):
                # Clear the session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

# Run the app
if __name__ == "__main__":
    main()

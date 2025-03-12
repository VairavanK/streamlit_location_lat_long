import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from io import BytesIO
import uuid
from PIL import Image
import streamlit.components.v1 as components
import numpy as np

# Set page config
st.set_page_config(page_title="Data Enrichment App", layout="wide")

# Add mobile-friendly styling with improved camera handling
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
    
    /* Enhanced camera button */
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
    
    /* Make camera smaller */
    .stCamera > div {
        max-height: 400px !important;
    }
    
    /* Camera container modifications */
    .camera-container {
        max-width: 500px !important;
        margin: 0 auto;
    }
    
    /* Make camera modal-like instead of page-shifting */
    .camera-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.8);
        z-index: 1000;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }
    
    .camera-content {
        background: white;
        border-radius: 10px;
        padding: 15px;
        width: 90%;
        max-width: 500px;
    }
    
    .camera-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .camera-close {
        cursor: pointer;
        font-size: 24px;
    }
</style>

<script>
// Force back camera selection for all camera inputs
function setupBackCamera() {
    // Find all video elements that get created by streamlit camera_input
    const videoElements = document.querySelectorAll('.stCamera video');
    videoElements.forEach(function(video) {
        if (video && !video.dataset.cameraInitialized) {
            // Get user media constraints for environment facing camera
            const constraints = {
                video: {
                    facingMode: { exact: "environment" }
                }
            };
            
            // Stop any existing stream
            if (video.srcObject) {
                const tracks = video.srcObject.getTracks();
                tracks.forEach(track => track.stop());
            }
            
            // Request camera with environment facing mode
            navigator.mediaDevices.getUserMedia(constraints)
                .then(function(stream) {
                    video.srcObject = stream;
                    video.dataset.cameraInitialized = 'true';
                })
                .catch(function(err) {
                    // If environment camera fails, fall back to any camera
                    console.log('Failed to get environment camera: ' + err);
                    navigator.mediaDevices.getUserMedia({ video: true })
                        .then(function(stream) {
                            video.srcObject = stream;
                            video.dataset.cameraInitialized = 'true';
                        });
                });
        }
    });
}

// Setup mutation observer to detect when camera is added to DOM
document.addEventListener('DOMContentLoaded', function() {
    // Setup observer to watch for camera elements being added
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                setupBackCamera();
            }
        });
    });
    
    // Start observing document for camera elements
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Also try immediately in case camera is already in DOM
    setTimeout(setupBackCamera, 1000);
});
</script>
""", unsafe_allow_html=True)

# Create directory for storing session data
try:
    UPLOAD_FOLDER = "uploaded_files"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
except PermissionError:
    import tempfile
    temp_dir = tempfile.gettempdir()
    UPLOAD_FOLDER = os.path.join(temp_dir, "uploaded_files")
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

# Session state initialization
if 'data' not in st.session_state:
    st.session_state.data = None
if 'selected_column' not in st.session_state:
    st.session_state.selected_column = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
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
if 'geolocation_data' not in st.session_state:
    st.session_state.geolocation_data = {}
if 'show_camera_modal' not in st.session_state:
    st.session_state.show_camera_modal = False
if 'current_value_for_camera' not in st.session_state:
    st.session_state.current_value_for_camera = None

# Function to compress and encode image to base64
def compress_and_encode_image(image_data, max_size=(800, 800), quality=75):
    try:
        # Open the image
        img = Image.open(BytesIO(image_data))
        
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

# Function to save session data to disk
def save_session_data():
    if st.session_state.data is not None:
        session_file = os.path.join(UPLOAD_FOLDER, f"session_{st.session_state.session_id}.csv")
        st.session_state.data.to_csv(session_file, index=False)

# Function to load session data from disk
def load_session_data():
    session_file = os.path.join(UPLOAD_FOLDER, f"session_{st.session_state.session_id}.csv")
    if os.path.exists(session_file):
        st.session_state.data = pd.read_csv(session_file)
        return True
    return False

# Function to generate a download link for the CSV
def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"enriched_data_{timestamp}.csv"
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="big-camera-button">Download Enriched CSV</a>'
    return href

# Save location data - Fixed to ensure location gets properly saved
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
        save_session_data()
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
                # Turn off camera after capture
                st.session_state.camera_active[value] = False
                st.session_state.show_camera_modal = False
                st.session_state.current_value_for_camera = None
                save_session_data()
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
    filtered = []
    for v in values:
        # Convert any value to string for searching
        v_str = str(v).lower()
        if search_term in v_str:
            filtered.append(v)
    return filtered

# Camera modal component for a better UX
def camera_modal(value):
    # Create a container for the modal-like camera UI
    st.markdown("""
    <div class="camera-overlay">
        <div class="camera-content">
            <div class="camera-header">
                <h3>Taking photo for: {}</h3>
                <span class="camera-close" onclick="closeModal()">×</span>
            </div>
            <div id="camera-placeholder"></div>
        </div>
    </div>
    
    <script>
    function closeModal() {{
        // Send a message to Streamlit to close the modal
        window.parent.postMessage({{
            type: "streamlit:setComponentValue",
            value: "close_camera_modal"
        }}, "*");
    }}
    </script>
    """.format(value), unsafe_allow_html=True)
    
    # Place the camera in the placeholder
    photo = st.camera_input("", key=f"modal_cam_{value}")
    
    # Add buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", key=f"modal_cancel_{value}"):
            st.session_state.show_camera_modal = False
            st.session_state.current_value_for_camera = None
            st.rerun()
    
    # Process the captured image
    if photo is not None:
        image_data = photo.getvalue()
        if save_image(value, image_data):
            st.success(f"Photo saved for {value}!")
            st.session_state.show_camera_modal = False
            st.session_state.current_value_for_camera = None
            st.rerun()

# Improved geolocation component with better Streamlit integration
def geolocation_component(value):
    # Create a unique key for this instance
    component_key = f"geoloc_{value}_{uuid.uuid4()}"
    
    # Use an HTML component with proper Streamlit message passing
    loc_data = components.html(
        f"""
        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;">
            <div id="status">Requesting your location...</div>
            <div id="coords" style="margin-top: 10px; display: none;">
                <div><strong>Latitude:</strong> <span id="lat"></span></div>
                <div><strong>Longitude:</strong> <span id="lng"></span></div>
                <div><strong>Accuracy:</strong> <span id="acc"></span> meters</div>
            </div>
        </div>

        <script>
            // Function to update status
            function updateStatus(message) {{
                document.getElementById('status').innerHTML = message;
            }}
            
            // Function to send data to Streamlit
            function sendToStreamlit(data) {{
                window.parent.postMessage({{
                    type: "streamlit:setComponentValue",
                    value: data
                }}, "*");
            }}
            
            // Function to get location
            function getLocation() {{
                updateStatus("<span style='color:blue;'>Requesting permission to access your location...</span>");
                
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(
                        // Success callback
                        function(position) {{
                            const lat = position.coords.latitude;
                            const lng = position.coords.longitude;
                            const accuracy = position.coords.accuracy;
                            
                            // Display values
                            document.getElementById('lat').textContent = lat;
                            document.getElementById('lng').textContent = lng;
                            document.getElementById('acc').textContent = accuracy;
                            document.getElementById('coords').style.display = 'block';
                            
                            // Display success
                            updateStatus("<span style='color:green;'>Location found! Coordinates:</span>");
                            
                            // Send to Streamlit with a slight delay to ensure UI updates first
                            setTimeout(function() {{
                                sendToStreamlit({{
                                    lat: lat,
                                    lng: lng,
                                    accuracy: accuracy,
                                    status: 'success'
                                }});
                            }}, 500);
                        }},
                        // Error callback
                        function(error) {{
                            let errorMsg = "";
                            switch(error.code) {{
                                case error.PERMISSION_DENIED:
                                    errorMsg = "Location permission denied by user.";
                                    break;
                                case error.POSITION_UNAVAILABLE:
                                    errorMsg = "Location information is unavailable.";
                                    break;
                                case error.TIMEOUT:
                                    errorMsg = "The request to get location timed out.";
                                    break;
                                default:
                                    errorMsg = "An unknown location error occurred.";
                            }}
                            updateStatus(`<span style='color:red;'>Error: ${{errorMsg}}</span>`);
                            sendToStreamlit({{ status: 'error', message: errorMsg }});
                        }},
                        // Options
                        {{
                            enableHighAccuracy: true,
                            timeout: 10000,
                            maximumAge: 0
                        }}
                    );
                }} else {{
                    const errorMsg = "Geolocation is not supported by this browser.";
                    updateStatus(`<span style='color:red;'>Error: ${{errorMsg}}</span>`);
                    sendToStreamlit({{ status: 'error', message: errorMsg }});
                }}
            }}
            
            // Start the location request immediately
            getLocation();
        </script>
        """,
        height=150,
        key=component_key
    )
    
    # Handle the returned location data
    if loc_data and isinstance(loc_data, dict) and 'status' in loc_data:
        if loc_data['status'] == 'success' and 'lat' in loc_data and 'lng' in loc_data:
            lat = loc_data['lat']
            lng = loc_data['lng']
            accuracy = loc_data.get('accuracy', 'unknown')
            
            # Save the location
            if save_location(value, lat, lng):
                st.success(f"Location saved for {value}: {lat}, {lng} (accuracy: {accuracy}m)")
                return True
        elif loc_data['status'] == 'error':
            st.error(f"Error getting location: {loc_data.get('message', 'Unknown error')}")
    
    # Cancel button
    if st.button("Cancel", key=f"cancel_geo_{value}"):
        return True
        
    return False

# Main app layout
st.title("Data Enrichment with Location and Images")

# Step 1: Upload CSV file or recover session
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file and st.session_state.data is None:
    try:
        st.session_state.data = pd.read_csv(uploaded_file)
        save_session_data()
        st.success("CSV file uploaded successfully!")
    except Exception as e:
        st.error(f"Error: {e}")
elif not uploaded_file and st.session_state.data is None:
    # Try to load from saved session
    if load_session_data():
        st.success("Recovered data from previous session!")

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
            
            save_session_data()
            st.rerun()
    
    # Step 3: Enrich each value
    if st.session_state.selected_column is not None:
        main_container = st.container()
        
        # Check if camera modal is active
        if st.session_state.show_camera_modal and st.session_state.current_value_for_camera:
            camera_modal(st.session_state.current_value_for_camera)
        else:
            # Main content
            with main_container:
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
                
                st.write("## Values to enrich")
                
                # Create tabs for "In Progress" and "Completed"
                in_progress_tab, completed_tab, all_tab = st.tabs(["In Progress", "Completed", "All Values"])
                
                # Helper functions for grouping values
                def get_in_progress_values():
                    values = []
                    for v in filtered_values:
                        loc_done = st.session_state.progress.get(v, {}).get('location', False)
                        img_done = st.session_state.progress.get(v, {}).get('image', False)
                        if not (loc_done and img_done):
                            values.append(v)
                    return values
                    
                def get_completed_values():
                    values = []
                    for v in filtered_values:
                        loc_done = st.session_state.progress.get(v, {}).get('location', False)
                        img_done = st.session_state.progress.get(v, {}).get('image', False)
                        if loc_done and img_done:
                            values.append(v)
                    return values
                
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
                                        if st.button(f"📍 Get Location for {value}", key=f"loc_{value}"):
                                            # Use the improved geolocation component
                                            if geolocation_component(value):
                                                st.rerun()
                                
                                with col2:
                                    img_status = "✅" if st.session_state.progress.get(value, {}).get('image', False) else "❌"
                                    st.write(f"Image: {img_status}")
                                    
                                    # Only show camera button if image not captured yet
                                    if not st.session_state.progress.get(value, {}).get('image', False):
                                        if st.button(f"📸 Take Photo for {value}", key=f"activate_{value}"):
                                            st.session_state.show_camera_modal = True
                                            st.session_state.current_value_for_camera = value
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
                                        if st.button(f"📍 Get Location for {value}", key=f"all_loc_{value}"):
                                            if geolocation_component(value):
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
                                        if st.button(f"📸 Take Photo for {value}", key=f"all_activate_{value}"):
                                            st.session_state.show_camera_modal = True
                                            st.session_state.current_value_for_camera = value
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
                    st.session_state.session_id = str(uuid.uuid4())
                    st.rerun()

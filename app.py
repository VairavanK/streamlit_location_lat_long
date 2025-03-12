import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from io import BytesIO
import uuid
from PIL import Image

# Set page config
st.set_page_config(page_title="Data Enrichment App", layout="wide")

# Add mobile-friendly styling and camera instructions
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
    
    /* Improve camera UI */
    .stCamera > button {
        background-color: #4CAF50 !important;
        color: white !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        border-radius: 5px !important;
        margin-top: 10px !important;
        width: 100% !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Create directory for storing session data if it doesn't exist
try:
    UPLOAD_FOLDER = "uploaded_files"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
except PermissionError:
    # Fall back to temp directory if permission issues
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

# Save location data
def save_location(value, lat, lng):
    if st.session_state.location_column is None:
        st.session_state.location_column = f"{st.session_state.selected_column}_location"
        if st.session_state.location_column not in st.session_state.data.columns:
            st.session_state.data[st.session_state.location_column] = None
    
    # Find the row index for the value
    row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column] == value].index
    if not row_idx.empty:
        st.session_state.data.loc[row_idx, st.session_state.location_column] = f"{lat}, {lng}"
        st.session_state.progress[value]['location'] = True
        save_session_data()
        st.success(f"Location saved for {value}: {lat}, {lng}")
        st.rerun()

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
            row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column] == value].index
            if not row_idx.empty:
                # Store base64 image directly in the dataframe
                st.session_state.data.loc[row_idx, st.session_state.image_column] = base64_image
                st.session_state.progress[value]['image'] = True
                save_session_data()
                st.success(f"Image saved for {value}")
                st.rerun()
        else:
            st.error("Failed to process image")
    except Exception as e:
        st.error(f"Error saving image: {e}")

# Display image from base64
def display_image_from_base64(base64_string, width=200):
    if base64_string and isinstance(base64_string, str) and base64_string.startswith('data:image'):
        st.markdown(f'<img src="{base64_string}" width="{width}">', unsafe_allow_html=True)
    else:
        st.write("No image available")

# Main app layout
st.title("Data Enrichment with Location and Images")

# Camera instructions - make this prominent
st.info("📱 **Mobile users**: Tap the camera switch icon during capture to use the back camera.")

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
            for value in st.session_state.data[st.session_state.selected_column].unique():
                if value not in st.session_state.progress:
                    st.session_state.progress[value] = {'location': False, 'image': False}
            
            save_session_data()
            st.rerun()
    
    # Step 3: Enrich each value
    if st.session_state.selected_column is not None:
        st.write(f"Enriching data for column: **{st.session_state.selected_column}**")
        
        unique_values = st.session_state.data[st.session_state.selected_column].unique()
        
        st.write("## Values to enrich")
        
        # Create tabs for "In Progress" and "Completed"
        in_progress_tab, completed_tab, all_tab = st.tabs(["In Progress", "Completed", "All Values"])
        
        # Helper functions for grouping values
        def get_in_progress_values():
            return [v for v in unique_values if not (
                st.session_state.progress.get(v, {}).get('location', False) and 
                st.session_state.progress.get(v, {}).get('image', False)
            )]
            
        def get_completed_values():
            return [v for v in unique_values if (
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
                                if st.button(f"Get Location for {value}", key=f"loc_{value}"):
                                    # Simulate getting geolocation - in real app this would use browser API
                                    st.write("Getting your location...")
                                    st.markdown("""
                                    <script>
                                    if (navigator.geolocation) {
                                        navigator.geolocation.getCurrentPosition(function(position) {
                                            const lat = position.coords.latitude;
                                            const lng = position.coords.longitude;
                                            // Use Streamlit callback to update
                                            window.parent.postMessage({
                                                type: "streamlit:setComponentValue",
                                                value: {"lat": lat, "lng": lng, "value": "%s"},
                                                dataType: "json"
                                            }, "*");
                                        });
                                    }
                                    </script>
                                    """ % value, unsafe_allow_html=True)
                                    
                                    # For demonstration, let's simulate location data
                                    # In a real app, you'd get this from the browser
                                    lat, lng = 37.7749, -122.4194
                                    save_location(value, lat, lng)
                        
                        with col2:
                            img_status = "✅" if st.session_state.progress.get(value, {}).get('image', False) else "❌"
                            st.write(f"Image: {img_status}")
                            
                            # Only show camera button if image not captured yet
                            if not st.session_state.progress.get(value, {}).get('image', False):
                                # Add a camera button with clear styling
                                st.markdown(
                                    f'<div class="big-camera-button">Take Photo for {value}</div>', 
                                    unsafe_allow_html=True
                                )
                                
                                # Standard camera input
                                img_file = st.camera_input(f"", key=f"cam_{value}")
                                if img_file is not None:
                                    # Make the image save process more robust
                                    try:
                                        # Get the image data
                                        image_data = img_file.getvalue()
                                        
                                        # Save image as base64
                                        save_image(value, image_data)
                                    except Exception as e:
                                        st.error(f"Error processing image: {e}")
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
                            row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column] == value].index[0]
                            loc_col = st.session_state.location_column
                            if loc_col and loc_col in st.session_state.data.columns:
                                loc_data = st.session_state.data.loc[row_idx, loc_col]
                                st.write(f"Saved location: {loc_data}")
                        
                        with col2:
                            st.write("Image: ✅")
                            row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column] == value].index[0]
                            img_col = st.session_state.image_column
                            if img_col and img_col in st.session_state.data.columns:
                                base64_image = st.session_state.data.loc[row_idx, img_col]
                                display_image_from_base64(base64_image)
            else:
                st.info("No completed values yet!")
                
        # All Values Tab
        with all_tab:
            for value in unique_values:
                location_done = st.session_state.progress.get(value, {}).get('location', False)
                image_done = st.session_state.progress.get(value, {}).get('image', False)
                status = "✅" if location_done and image_done else "🔄"
                
                with st.expander(f"{value} {status}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        loc_status = "✅" if location_done else "❌"
                        st.write(f"Location: {loc_status}")
                        
                        if not location_done:
                            if st.button(f"Get Location for {value}", key=f"all_loc_{value}"):
                                # Simulate getting geolocation - in real app this would use browser API
                                st.write("Getting your location...")
                                # For demo purposes
                                lat, lng = 37.7749, -122.4194
                                save_location(value, lat, lng)
                        else:
                            row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column] == value].index[0]
                            loc_col = st.session_state.location_column
                            if loc_col and loc_col in st.session_state.data.columns:
                                loc_data = st.session_state.data.loc[row_idx, loc_col]
                                st.write(f"Saved location: {loc_data}")
                    
                    with col2:
                        img_status = "✅" if image_done else "❌"
                        st.write(f"Image: {img_status}")
                        
                        if not image_done:
                            # Add a camera button with clear styling
                            st.markdown(
                                f'<div class="big-camera-button">Take Photo for {value}</div>', 
                                unsafe_allow_html=True
                            )
                            
                            # Standard camera input
                            img_file = st.camera_input(f"", key=f"all_cam_{value}")
                            if img_file is not None:
                                try:
                                    image_data = img_file.getvalue()
                                    save_image(value, image_data)
                                except Exception as e:
                                    st.error(f"Error processing image: {e}")
                        else:
                            row_idx = st.session_state.data[st.session_state.data[st.session_state.selected_column] == value].index[0]
                            img_col = st.session_state.image_column
                            if img_col and img_col in st.session_state.data.columns:
                                base64_image = st.session_state.data.loc[row_idx, img_col]
                                display_image_from_base64(base64_image)
        
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

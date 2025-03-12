# Data Enrichment Streamlit App

A Streamlit application for enriching CSV data with location information and images.

## Features
- Upload a CSV file
- Select a column to enrich
- Capture location data for each value
- Take photos for each value
- Download the enriched data
- Session persistence to prevent data loss

## How to Use
1. Upload your CSV file
2. Select the column you want to enrich
3. For each value in the column:
   - Click "Get Location" to add location data
   - Use the camera button to take a photo
4. Download the enriched data when finished

## Installation
```bash
pip install -r requirements.txt
streamlit run app.py

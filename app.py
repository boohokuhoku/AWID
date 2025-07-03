import streamlit as st
import re
import pandas as pd

# Function to process AW IDs and return unique numeric AW IDs
def get_unique_aw_ids(input_data):
    # Split input by newlines and strip whitespace
    lines = [line.strip() for line in input_data.split('\n') if line.strip()]
    # Skip the header row
    data_lines = lines[1:]
    # Collect all numeric AW IDs
    all_aw_ids = []
    for line in data_lines:
        tokens = line.split('\t')
        # Process AW IDs from columns 2 onward (skip NAME and Preview columns)
        aw_id_columns = tokens[2:] if len(tokens) > 2 else []
        # Filter numeric AW IDs
        numeric_ids = [token.strip() for token in aw_id_columns if token.strip().isdigit()]
        all_aw_ids.extend(numeric_ids)
    # Remove duplicates while preserving order
    unique_aw_ids = list(dict.fromkeys(all_aw_ids))
    return unique_aw_ids

# Function to process tab-separated input for table generation
def process_input(input_data):
    # Split input by newlines and strip whitespace
    lines = [line.strip() for line in input_data.split('\n') if line.strip()]
    
    # Initialize lists for the table
    aw_ids = []
    artwork_names = []
    short_urls = []
    name_count = {}
    
    # Process each data line (skip header)
    for line in lines[1:]:  # Skip the header row
        tokens = line.split('\t')
        if not tokens or len(tokens) < 2:
            continue  # Skip empty or invalid lines
        
        artwork_name = tokens[0].strip()  # First column is the artwork name
        if not artwork_name:
            continue  # Skip if no artwork name
        
        # Process AW IDs from columns 2 onward (skip Preview column)
        aw_id_columns = tokens[2:] if len(tokens) > 2 else []
        
        # Filter unique numeric AW IDs in this row
        unique_ids = list(dict.fromkeys([token.strip() for token in aw_id_columns if token.strip().isdigit()]))
        
        for aw_id in unique_ids:
            aw_ids.append(aw_id)
            artwork_names.append(artwork_name)
            
            # Generate short URL for the artwork name
            clean_name = re.sub(r'[^\w\s]', ' ', artwork_name.lower()).strip()
            slug = '-'.join(clean_name.split())
            
            # Handle duplicates
            if slug in name_count:
                name_count[slug] += 1
                short_urls.append(f"{slug}-atwgp{name_count[slug]}")
            else:
                name_count[slug] = 0
                short_urls.append(slug)
    
    # Create DataFrame
    df = pd.DataFrame({
        'AW ID': aw_ids,
        'Artwork Name': artwork_names,
        'Short URL': short_urls
    })
    
    return df

# Streamlit app layout
st.title("Artwork ID and URL Generator")

# Input section for tab-separated data
st.header("Input Processor")
input_data = st.text_area("Enter tab-separated data (including headers):", 
                         value="""NAME\tPreview (Suggested model for web display)\tiPhone/TA\tArtwork ID\tHuawei M60/M60 pro Artwork ID\tHuawei M70/M70 pro Artwork ID\tHuawei P70/P70 pro/P70 pro+ Artwork ID\tHuawei P70 Ultra Artwork ID\tHuawei Pocket 2 Artwork ID\tHuawei PuraX Artwork ID\tGalaxy S Series Artwork ID\tGalaxy Z Fold 6-5 Artwork ID\tGalaxy Z Flip 7-5 Artwork ID\tGalaxy Z Flip 4 Artwork ID\tGoogle Pixel 9-8 Artwork ID\tGoogle Pixel 9 Pro Fold Artwork ID\tGoogle Pixel Fold Artwork ID
Symbol Mosaic Case (Retail Exclusive)\t\t35221837\t35226788\t35226788\t35221837\t35226788\t35226790\tDisabled\t35221837\t35226788\tDisabled\tDisabled\t35221837\t35221837\tDisabled
Dialect Wave Case (Retail Exclusive)\t\t35207137\t35207351\t35207351\t35207351\t35207351\t35207375\tDisabled\t35207351\t35207351\tDisabled\tDisabled\t35207351\t35207351\tDisabled
Pattern Whisper Case (Retail Exclusive)\t\t35211989\t35212045\t35212045\t35212045\t35212045\t35212048\tDisabled\t35211989\t35211989\tDisabled\tDisabled\t35211989\t35211989\t35211989
Linear Passage Case (Retail Exclusive)\t\t35207147\t35207147\t35207147\t35207147\t35207147\t35207365\tDisabled\t35207147\t35207147\tDisabled\tDisabled\t35207147\t35207147\t35207147
Symbol Mosaic Snappy Grip Stand (Retail Exclusive)\t\t35221900
Pattern Whisper Snappy Grip Stand (Retail Exclusive)\t\t35212088
Symbol Mosaic Snappy Grip Holder (Retail Exclusive)\t\t35221903
Linear Passage Earbuds Case (Retail Exclusive)\t\t35207266
Symbol Mosaic Tablet Case (Retail Exclusive)\t\t35221897
Pattern Whisper Snappy Cardholder Stand (Retail Exclusive)\t\t35212085
Dialect Wave Snappy Wallet (Retail Exclusive)\t\t35207288""")

# Section for unique AW IDs
st.header("Unique AW ID Processor")
if st.button("Process Unique AW IDs"):
    if input_data:
        unique_aw_ids = get_unique_aw_ids(input_data)
        if unique_aw_ids:
            st.subheader("Unique Numeric AW IDs:")
            st.text('\n'.join(unique_aw_ids))
        else:
            st.error("No valid numeric AW IDs found.")
    else:
        st.error("Please enter tab-separated data.")

# Section for generating table
st.header("AW ID and Short URL Table")
if st.button("Generate Table"):
    if input_data:
        df = process_input(input_data)
        if not df.empty:
            st.subheader("Generated Table:")
            st.dataframe(df)
            
            # Convert table to plain text for copying
            table_text = df.to_string(index=False)
            
            # Create a button to copy the table content
            st.text_area("Copyable Table Content:", table_text, height=150)
            st.markdown("""
                <script>
                function copyToClipboard() {
                    const text = document.getElementById('copyable-text').value;
                    navigator.clipboard.writeText(text).then(() => {
                        alert('Table copied to clipboard!');
                    });
                }
                </script>
                <textarea id="copyable-text" style="display:none;">{}</textarea>
                <button onclick="copyToClipboard()">Copy Table to Clipboard</button>
            """.format(table_text), unsafe_allow_html=True)
        else:
            st.error("No valid numeric AW IDs or artwork names provided.")
    else:
        st.error("Please provide tab-separated data.")
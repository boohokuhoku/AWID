import streamlit as st
import re
import pandas as pd

# Function to clean artwork name to include only English (ASCII) characters
def clean_artwork_name(name):
    # Remove non-ASCII (non-English) characters, keep letters, digits, spaces, and basic punctuation
    clean_name = re.sub(r'[^\x00-\x7F]+', '', name).strip()
    return clean_name

# Function to process input and extract unique AW IDs with corresponding artwork names
def process_input(input_text):
    # Split input by newlines and strip whitespace
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    aw_id_name_pairs = []
    
    # Parse each line for artwork name and AW IDs
    for line in lines:
        # Split by tabs, expect at least two columns
        columns = re.split(r'\t+', line)
        if len(columns) >= 2:
            # Clean artwork name to remove non-English characters for output
            artwork_name = clean_artwork_name(columns[0].strip())
            if artwork_name:  # Only process if cleaned name is not empty
                # Split AW IDs by commas or spaces, filter for numeric IDs
                aw_ids = [token.strip() for token in re.split(r'[,\s]+', columns[1]) if token.strip() and token.isdigit()]
                for aw_id in aw_ids:
                    aw_id_name_pairs.append((aw_id, artwork_name))
    
    # Remove duplicate AW IDs while preserving order and keeping the first associated artwork name
    unique_aw_ids = []
    seen_aw_ids = set()
    for aw_id, artwork_name in aw_id_name_pairs:
        if aw_id not in seen_aw_ids:
            unique_aw_ids.append((aw_id, artwork_name))
            seen_aw_ids.add(aw_id)
    
    return unique_aw_ids

# Function to generate short URLs from artwork names
def generate_short_urls(artwork_names):
    short_urls = []
    name_count = {}
    
    for name in artwork_names:
        # Use cleaned name (already cleaned in process_input)
        clean_name = name  # Name is already cleaned from process_input
        if clean_name:  # Only process if name is not empty
            # Convert to lowercase, replace special characters with spaces, and split
            clean_name = re.sub(r'[^\w\s]', ' ', clean_name.lower()).strip()
            # Replace multiple spaces with single space and then replace spaces with hyphens
            slug = '-'.join(clean_name.split())
            
            # Handle duplicates to match format: e.g., absolutely-no-problem-phone-cases, absolutely-no-problem-phone-cases-atwgp1, etc.
            if slug in name_count:
                name_count[slug] += 1
                short_urls.append(f"{slug}-atwgp{name_count[slug]}")
            else:
                name_count[slug] = 0
                short_urls.append(slug)
        else:
            short_urls.append("")  # Empty URL for empty names (shouldn't occur due to process_input filter)
    
    return short_urls

# Function to create a table from AW IDs, artwork names, and short URLs
def create_id_name_url_table(aw_ids, artwork_names, short_urls):
    # Create DataFrame
    df = pd.DataFrame({
        'AW ID': aw_ids,
        'Artwork Name': artwork_names,
        'Short URL': short_urls
    })
    return df

# Streamlit app layout
st.title("Artwork ID and URL Generator")

# Input section for Artwork Names and AW IDs
st.header("Artwork Name and AW ID Input")
st.write("Enter two tab-separated columns: Artwork Name (can include non-English text, which will be removed in output) and AW IDs (one pair per line). AW IDs can include non-numeric tokens (e.g., Disabled), but only numeric IDs are processed.")
input_text = st.text_area("Artwork Names and AW IDs:", 
                         placeholder="e.g., Absolutely No Problem Phone Cases 特殊字符\t35221837,35226788,Disabled\nAnother Artwork Name テスト\t35207351,Disabled")
if st.button("Generate Table"):
    if input_text:
        unique_aw_id_pairs = process_input(input_text)
        if unique_aw_id_pairs:
            # Extract AW IDs and artwork names
            aw_ids = [pair[0] for pair in unique_aw_id_pairs]
            artwork_names = [pair[1] for pair in unique_aw_id_pairs]
            # Generate short URLs from cleaned artwork names
            short_urls = generate_short_urls(artwork_names)
            
            # Create and display table
            df = create_id_name_url_table(aw_ids, artwork_names, short_urls)
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
            st.error("No valid numeric AW IDs or valid English artwork names found in the input.")
    else:
        st.error("Please enter at least one line with an artwork name and AW IDs.")

import streamlit as st
import re
import pandas as pd

# Function to process input and extract unique AW IDs
def process_input(input_text):
    # Split input by newlines and strip whitespace
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    aw_ids = []
    
    # Parse each line for AW IDs
    for line in lines:
        # Filter for numeric IDs
        if line.isdigit():
            aw_ids.append(line)
    
    # Remove duplicate AW IDs while preserving order
    unique_aw_ids = []
    seen_aw_ids = set()
    for aw_id in aw_ids:
        if aw_id not in seen_aw_ids:
            unique_aw_ids.append(aw_id)
            seen_aw_ids.add(aw_id)
    
    # Format as comma-separated string
    return ', '.join(unique_aw_ids)

# Function to generate short URLs from artwork names
def generate_short_urls(artwork_names):
    short_urls = []
    name_count = {}
    
    for name in artwork_names:
        # Convert to lowercase, replace special characters with spaces, and split
        clean_name = re.sub(r'[^\w\s]', ' ', name.lower()).strip()
        # Replace multiple spaces with single space and then replace spaces with hyphens
        slug = '-'.join(clean_name.split())
        
        # Handle duplicates to match format: e.g., absolutely-no-problem-phone-cases, absolutely-no-problem-phone-cases-atwgp1, etc.
        if slug in name_count:
            name_count[slug] += 1
            short_urls.append(f"{slug}-atwgp{name_count[slug]}")
        else:
            name_count[slug] = 0
            short_urls.append(slug)
    
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

# Function to create a table with only unique AW IDs
def create_id_table(aw_ids):
    # Create DataFrame
    df = pd.DataFrame({
        'AW ID': aw_ids
    })
    return df

# Function to format unique AW IDs for PDP
def process_for_pdp(aw_ids):
    # Join unique AW IDs with commas and spaces
    return ', '.join(aw_ids)

# Streamlit app layout
st.title("Artwork ID and URL Generator")

# Input section for Artwork Names and AW IDs
st.header("Artwork Name and AW ID Input")
st.write("Enter two tab-separated columns: Artwork Name and AW IDs (one pair per line). AW IDs can include non-numeric tokens (e.g., Disabled), but only numeric IDs are processed.")
input_text_name_id = st.text_area("Artwork Names and AW IDs:", 
                                 placeholder="e.g., Absolutely No Problem Phone Cases\t35221837,35226788,Disabled\nAnother Artwork Name\t35207351,Disabled")

# Input section for AW IDs only
st.header("AW ID Input for PDP")
st.write("Enter one AW ID per line.")
input_text_ids = st.text_area("AW IDs:", 
                              placeholder="e.g., 35167317\n35175930\n35221240")

# Button to generate table with AW IDs, Artwork Names, and Short URLs
if st.button("Generate Full Table"):
    if input_text_name_id:
        # Process input as before
        lines = [line.strip() for line in input_text_name_id.split('\n') if line.strip()]
        aw_id_name_pairs = []
        
        for line in lines:
            columns = re.split(r'\t+', line)
            if len(columns) >= 2:
                artwork_name = columns[0].strip()
                aw_ids = [token.strip() for token in re.split(r'[,\s]+', columns[1]) if token.strip() and token.isdigit()]
                for aw_id in aw_ids:
                    aw_id_name_pairs.append((aw_id, artwork_name))
        
        if aw_id_name_pairs:
            # Remove duplicates
            unique_aw_id_pairs = []
            seen_aw_ids = set()
            for aw_id, artwork_name in aw_id_name_pairs:
                if aw_id not in seen_aw_ids:
                    unique_aw_id_pairs.append((aw_id, artwork_name))
                    seen_aw_ids.add(aw_id)
            
            # Extract AW IDs and artwork names
            aw_ids = [pair[0] for pair in unique_aw_id_pairs]
            artwork_names = [pair[1] for pair in unique_aw_id_pairs]
            # Generate short URLs from artwork names
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
            st.error("No valid numeric AW IDs found in the input.")
    else:
        st.error("Please enter at least one line with an artwork name and AW IDs.")

# Button to generate table with only unique AW IDs
if st.button("Generate Unique AW IDs"):
    if input_text_name_id:
        # Process input as before
        lines = [line.strip() for line in input_text_name_id.split('\n') if line.strip()]
        aw_id_name_pairs = []
        
        for line in lines:
            columns = re.split(r'\t+', line)
            if len(columns) >= 2:
                artwork_name = columns[0].strip()
                aw_ids = [token.strip() for token in re.split(r'[,\s]+', columns[1]) if token.strip() and token.isdigit()]
                for aw_id in aw_ids:
                    aw_id_name_pairs.append((aw_id, artwork_name))
        
        if aw_id_name_pairs:
            # Remove duplicates
            unique_aw_id_pairs = []
            seen_aw_ids = set()
            for aw_id, artwork_name in aw_id_name_pairs:
                if aw_id not in seen_aw_ids:
                    unique_aw_id_pairs.append((aw_id, artwork_name))
                    seen_aw_ids.add(aw_id)
            
            # Extract AW IDs
            aw_ids = [pair[0] for pair in unique_aw_id_pairs]
            
            # Create and display table
            df = create_id_table(aw_ids)
            st.subheader("Unique AW IDs:")
            st.dataframe(df)
            
            # Convert table to plain text for copying
            table_text = df.to_string(index=False)
            
            # Create a button to copy the table content
            st.text_area("Copyable Unique AW IDs:", table_text, height=150)
            st.markdown("""
                <script>
                function copyToClipboardUnique() {
                    const text = document.getElementById('copyable-text-unique').value;
                    navigator.clipboard.writeText(text).then(() => {
                        alert('Unique AW IDs copied to clipboard!');
                    });
                }
                </script>
                <textarea id="copyable-text-unique" style="display:none;">{}</textarea>
                <button onclick="copyToClipboardUnique()">Copy Unique AW IDs to Clipboard</button>
            """.format(table_text), unsafe_allow_html=True)
        else:
            st.error("No valid numeric AW IDs found in the input.")
    else:
        st.error("Please enter at least one line with an artwork name and AW IDs.")

# Button to generate PDP formatted AW IDs
if st.button("Process for PDP"):
    if input_text_ids:
        pdp_text = process_input(input_text_ids)
        if pdp_text:
            st.subheader("PDP Formatted AW IDs:")
            st.text(pdp_text)
            
            # Create a button to copy the PDP text
            st.text_area("Copyable PDP AW IDs:", pdp_text, height=100)
            st.markdown("""
                <script>
                function copyToClipboardPDP() {
                    const text = document.getElementById('copyable-text-pdp').value;
                    navigator.clipboard.writeText(text).then(() => {
                        alert('PDP AW IDs copied to clipboard!');
                    });
                }
                </script>
                <textarea id="copyable-text-pdp" style="display:none;">{}</textarea>
                <button onclick="copyToClipboardPDP()">Copy PDP AW IDs to Clipboard</button>
            """.format(pdp_text), unsafe_allow_html=True)
        else:
            st.error("No valid numeric AW IDs found in the input.")
    else:
        st.error("Please enter at least one AW ID.")
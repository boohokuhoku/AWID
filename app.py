import streamlit as st
import re
import pandas as pd

# Function to process AW IDs
def get_unique_aw_ids(aw_ids_input):
    # Split input by commas, newlines, or tabs, strip whitespace, and filter out empty strings
    tokens = [token.strip() for token in re.split(r'[,\n\t]+', aw_ids_input) if token.strip()]
    # Filter for numeric IDs only
    numeric_ids = [token for token in tokens if token.isdigit()]
    # Remove duplicates while preserving order
    unique_ids = list(dict.fromkeys(numeric_ids))
    return unique_ids

# Function to generate short URLs from artwork names
def generate_short_urls(artwork_names_input):
    # Split input by newlines, strip whitespace, and filter out empty strings
    artwork_names = [name.strip() for name in artwork_names_input.split('\n') if name.strip()]
    short_urls = []
    name_count = {}
    
    for name in artwork_names:
        # Convert to lowercase, replace special characters with spaces, and split
        clean_name = re.sub(r'[^\w\s]', ' ', name.lower()).strip()
        # Replace multiple spaces with single space and then replace spaces with hyphens
        slug = '-'.join(clean_name.split())
        
        # Handle duplicates
        if slug in name_count:
            name_count[slug] += 1
            # For duplicates: second occurrence gets -atwgp1, third gets -atwgp2, etc.
            short_urls.append(f"{slug}-atwgp{name_count[slug]}")
        else:
            name_count[slug] = 0
            # First occurrence gets no suffix
            short_urls.append(slug)
    
    return short_urls

# Function to create a table from AW IDs and short URLs
def create_id_url_table(aw_ids, short_urls):
    # Ensure equal lengths by truncating to the shorter length
    min_length = min(len(aw_ids), len(short_urls))
    aw_ids = aw_ids[:min_length]
    short_urls = short_urls[:min_length]
    
    # Create DataFrame
    df = pd.DataFrame({
        'AW ID': aw_ids,
        'Short URL': short_urls
    })
    return df

# Streamlit app layout
st.title("Artwork ID and URL Generator")

# Input section for AW IDs
st.header("AW ID Processor")
aw_ids_input = st.text_area("Enter AW IDs (tab, comma, or newline-separated):")
if st.button("Process AW IDs"):
    if aw_ids_input:
        unique_aw_ids = get_unique_aw_ids(aw_ids_input)
        if unique_aw_ids:
            st.subheader("Unique AW IDs:")
            st.text('\n'.join(unique_aw_ids))
        else:
            st.error("No valid numeric AW IDs found.")
    else:
        st.error("Please enter at least one AW ID.")

# Input section for Artwork Names
st.header("Artwork Name to Short URL")
artwork_names_input = st.text_area("Enter artwork names (one per line):")
if st.button("Generate Short URLs"):
    if artwork_names_input:
        short_urls = generate_short_urls(artwork_names_input)
        st.subheader("Generated Short URLs:")
        st.text('\n'.join(short_urls))
    else:
        st.error("Please enter at least one artwork name.")

# Section for generating and copying table
st.header("AW ID and Short URL Table")
if st.button("Generate Table"):
    if aw_ids_input and artwork_names_input:
        unique_aw_ids = get_unique_aw_ids(aw_ids_input)
        short_urls = generate_short_urls(artwork_names_input)
        if unique_aw_ids and short_urls:
            df = create_id_url_table(unique_aw_ids, short_urls)
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
            st.error("No valid AW IDs or artwork names provided.")
    else:
        st.error("Please provide both AW IDs and artwork names.")
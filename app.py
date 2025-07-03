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

# Function to compare tables and highlight differences
def compare_tables(generated_df, comparison_input):
    # Parse comparison input into DataFrame
    comparison_lines = [line.strip() for line in comparison_input.split('\n') if line.strip()]
    if not comparison_lines:
        return generated_df, []
    
    # Assume first line is header
    header = comparison_lines[0].split('\t')
    data = [line.split('\t') for line in comparison_lines[1:]]
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame(data, columns=header[:3])  # Take first 3 columns: AW ID, Artwork Name, Short URL
    comparison_df = comparison_df[['AW ID', 'Artwork Name', 'Short URL']].dropna()
    
    # Ensure AW ID is string for comparison
    generated_df['AW ID'] = generated_df['AW ID'].astype(str)
    comparison_df['AW ID'] = comparison_df['AW ID'].astype(str)
    
    # Merge DataFrames to compare
    merged_df = generated_df.merge(comparison_df, how='outer', indicator=True, suffixes=('_gen', '_comp'))
    
    # Identify differing rows
    diff_rows = []
    for idx, row in merged_df.iterrows():
        if row['_merge'] != 'both':
            diff_rows.append(idx)
        else:
            # Check if any column differs
            if (row['AW ID_gen'] != row['AW ID_comp'] or 
                row['Artwork Name_gen'] != row['Artwork Name_comp'] or 
                row['Short URL_gen'] != row['Short URL_comp']):
                diff_rows.append(idx)
    
    # Create styled DataFrame for display
    styled_df = generated_df.copy()
    def highlight_diff(row):
        if row.name in diff_rows:
            return ['background-color: #ffcccc' for _ in row]
        return ['background-color: white' for _ in row]
    
    styled_df = styled_df.style.apply(highlight_diff, axis=1)
    
    return styled_df, diff_rows

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
        generated_df = process_input(input_data)
        if not generated_df.empty:
            st.subheader("Generated Table:")
            st.dataframe(generated_df)
            
            # Convert table to plain text for copying
            table_text = generated_df.to_string(index=False)
            
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
            
            # Store generated table in session state for comparison
            st.session_state['generated_df'] = generated_df
        else:
            st.error("No valid numeric AW IDs or artwork names provided.")
    else:
        st.error("Please provide tab-separated data.")

# Section for table comparison
st.header("Table Comparison")
comparison_input = st.text_area("Enter comparison table (tab-separated, with headers AW ID, Artwork Name, Short URL):", 
                               value="""AW ID\tArtwork Name\tShort URL
35221837\tSymbol Mosaic Case (Retail Exclusive)\tsymbol-mosaic-case-retail-exclusive
35226788\tSymbol Mosaic Case (Retail Exclusive)\tsymbol-mosaic-case-retail-exclusive-atwgp1
35226790\tSymbol Mosaic Case (Retail Exclusive)\tsymbol-mosaic-case-retail-exclusive-atwgp2
35207137\tDialect Wave Case (Retail Exclusive)\tdialect-wave-case-retail-exclusive
35207351\tDialect Wave Case (Retail Exclusive)\tdialect-wave-case-retail-exclusive-atwgp1
35207375\tDialect Wave Case (Retail Exclusive)\tdialect-wave-case-retail-exclusive-atwgp2""")

if st.button("Compare Tables"):
    if 'generated_df' in st.session_state and comparison_input:
        styled_df, diff_rows = compare_tables(st.session_state['generated_df'], comparison_input)
        if not styled_df.data.empty:
            st.subheader("Comparison Table (Differences Highlighted in Red):")
            st.dataframe(styled_df)
            if diff_rows:
                st.write(f"Rows with differences (indices): {diff_rows}")
            else:
                st.write("No differences found.")
        else:
            st.error("No valid data in comparison table.")
    else:
        st.error("Please generate a table first and provide a comparison table.")
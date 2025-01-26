import streamlit as st
import openai
from datetime import datetime
import pandas as pd
import time

def setup_page():
    """Configure the basic Streamlit page layout and settings"""
    st.set_page_config(page_title="AI Rank Tracker", layout="wide")
    st.title("AI Search Rank Tracker")
    st.write("Track your brand's position in AI search results")

def initialize_openai():
    """Initialize OpenAI client with API key from Streamlit secrets"""
    api_key = st.text_input("Enter your OpenAI API key", type="password")
    if api_key:
        return openai.OpenAI(api_key=api_key)
    return None

def check_brand_mentions(response_text, brand_name):
    """
    Analyze where and how a brand is mentioned in the AI response
    Returns position (early, middle, late) and the context around the mention
    """
    # Convert to lowercase for case-insensitive matching
    response_lower = response_text.lower()
    brand_lower = brand_name.lower()
    
    # Find the position of the brand mention
    if brand_lower in response_lower:
        # Split response into thirds to determine position
        total_length = len(response_lower)
        first_third = total_length // 3
        second_third = 2 * (total_length // 3)
        
        position = response_lower.find(brand_lower)
        
        if position < first_third:
            mention_position = "Early (Top 3)"
        elif position < second_third:
            mention_position = "Middle"
        else:
            mention_position = "Late"
            
        # Extract context (50 characters before and after the mention)
        start = max(0, position - 50)
        end = min(len(response_text), position + len(brand_name) + 50)
        context = response_text[start:end]
        
        return mention_position, context
    
    return "Not mentioned", "Brand not found in response"

def main():
    setup_page()
    
    # Initialize OpenAI client
    client = initialize_openai()
    if not client:
        st.warning("Please enter your OpenAI API key to continue")
        return
    
    # Get user inputs
    brand_name = st.text_input("Enter your brand name:")
    keywords = st.text_area("Enter keywords (one per line):")
    
    if st.button("Track Rankings") and brand_name and keywords:
        # Convert keywords text area into list
        keyword_list = [k.strip() for k in keywords.split('\n') if k.strip()]
        
        # Prepare results storage
        results = []
        
        # Progress bar
        progress_bar = st.progress(0)
        
        for idx, keyword in enumerate(keyword_list):
            st.write(f"Checking keyword: {keyword}")
            
            try:
                # Create a search-like prompt
                prompt = f"What are the best {keyword}? Please provide a comprehensive list with brief descriptions."
                
                # Make API call to OpenAI
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful shopping assistant providing product recommendations."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Get the response text
                response_text = response.choices[0].message.content
                
                # Analyze the response
                position, context = check_brand_mentions(response_text, brand_name)
                
                # Store results
                results.append({
                    'Keyword': keyword,
                    'Position': position,
                    'Context': context,
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Update progress
                progress_bar.progress((idx + 1) / len(keyword_list))
                
                # Avoid rate limits
                time.sleep(1)
                
            except Exception as e:
                st.error(f"Error processing keyword '{keyword}': {str(e)}")
        
        # Display results
        if results:
            df = pd.DataFrame(results)
            st.write("### Ranking Results")
            st.dataframe(df)
            
            # Download button for results
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Results",
                csv,
                "ai_rankings.csv",
                "text/csv",
                key='download-csv'
            )

if __name__ == "__main__":
    main()

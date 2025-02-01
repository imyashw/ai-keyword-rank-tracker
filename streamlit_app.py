import streamlit as st
import openai
import time
import pandas as pd
from typing import List, Dict

def validate_keyword(keyword: str) -> bool:
    """
    Validate if the keyword is specific enough.
    Returns True if keyword is specific, False otherwise.
    """
    # Split keyword into words
    words = keyword.lower().split()
    
    # Check if keyword has at least 4 words and contains specific terms
    if len(words) < 4:
        return False
    
    # Add more specific checks based on your requirements
    return True

def search_openai(keyword: str, api_key: str) -> List[Dict]:
    """
    Search using OpenAI API and return results
    """
    try:
        client = openai.Client(api_key=api_key)
        
        # Construct a prompt that asks for search results
        prompt = f"""Please provide a list of top 10 relevant results for the search term: "{keyword}"
        Format each result as: [Brand/Company Name] - [Brief Description]
        Focus on actual businesses and brands that match this query."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a search engine providing accurate, relevant results."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Extract and parse the results
        results_text = response.choices[0].message.content
        results = results_text.strip().split('\n')
        
        # Clean and structure the results
        parsed_results = []
        for idx, result in enumerate(results, 1):
            if result.strip():
                parsed_results.append({
                    'rank': idx,
                    'result': result.strip()
                })
        
        return parsed_results
    
    except Exception as e:
        st.error(f"Error occurred while searching: {str(e)}")
        return []

def analyze_rankings(results: List[Dict], target_brand: str) -> Dict:
    """
    Analyze the rankings for mentions of the target brand
    """
    analysis = {
        'found': False,
        'rank': None,
        'context': None
    }
    
    target_brand = target_brand.lower()
    for result in results:
        if target_brand in result['result'].lower():
            analysis['found'] = True
            analysis['rank'] = result['rank']
            analysis['context'] = result['result']
            break
    
    return analysis

def main():
    st.title("Keyword Ranking Analysis Tool")
    
    # Add description and instructions
    st.write("""
    This tool analyzes search rankings for specific keywords related to your brand.
    Please provide specific, detailed keywords for better results.
    
    Example of a good keyword: "best plus size women's clothing brands in Mumbai"
    Example of a poor keyword: "clothing brands"
    """)
    
    # Input fields
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    target_brand = st.text_input("Enter your brand name")
    keyword = st.text_input("Enter your specific keyword to analyze")
    
    if st.button("Analyze Rankings"):
        if not api_key or not keyword or not target_brand:
            st.warning("Please fill in all fields.")
            return
        
        # Validate keyword
        if not validate_keyword(keyword):
            st.warning("""
            Please enter a more specific keyword. Your keyword should:
            - Be at least 4 words long
            - Include specific details (location, category, etc.)
            - Be relevant to your brand
            """)
            return
        
        with st.spinner("Analyzing rankings..."):
            # Perform the search
            results = search_openai(keyword, api_key)
            
            if results:
                # Analyze rankings
                analysis = analyze_rankings(results, target_brand)
                
                # Display results
                st.subheader("Search Results")
                df = pd.DataFrame(results)
                st.dataframe(df)
                
                st.subheader("Brand Analysis")
                if analysis['found']:
                    st.success(f"Your brand was found at rank {analysis['rank']}")
                    st.write("Context:", analysis['context'])
                else:
                    st.warning("Your brand was not found in the top results.")
                    st.write("Consider:")
                    st.write("- Optimizing your brand's online presence")
                    st.write("- Using different keyword variations")
                    st.write("- Focusing on more specific geographic or niche markets")

if __name__ == "__main__":
    main()

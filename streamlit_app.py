import streamlit as st
import pandas as pd
from openai import OpenAI
from typing import List, Dict

# Page config
st.set_page_config(
    page_title="Keyword Ranking Analysis Tool",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'openai_client' not in st.session_state:
    st.session_state.openai_client = None

def validate_keyword(keyword: str) -> bool:
    """Validate if the keyword follows common search patterns"""
    if not keyword:
        return False
        
    keyword_lower = keyword.lower()
    words = keyword_lower.split()
    
    # Check for comparison patterns
    has_comparison = "vs" in words or "versus" in words
    
    # Check for basic qualifying words
    qualifiers = ["best", "top", "free", "pricing", "alternatives", "how"]
    has_qualifier = any(word in words for word in qualifiers)
    
    # Accept if it's a comparison, has qualifier, or minimum 3 words
    return has_comparison or has_qualifier or len(words) >= 3

def search_openai(keyword: str) -> List[Dict]:
    """Search using OpenAI API and return results"""
    if not st.session_state.openai_client:
        st.error("OpenAI client not initialized. Please check your API key.")
        return []
    
    try:
        prompt = f"""Please provide a list of top 10 relevant results for the search term: "{keyword}"
        Format each result as: [Brand/Company Name] - [Brief Description]
        Focus on actual businesses and brands that match this query.
        Ensure results are numbered 1-10."""
        
        response = st.session_state.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a search engine providing accurate, relevant results."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        results_text = response.choices[0].message.content
        results = results_text.strip().split('\n')
        
        parsed_results = []
        for idx, result in enumerate(results, 1):
            if result.strip():
                cleaned_result = result.strip()
                if '. ' in cleaned_result[:4]:
                    cleaned_result = cleaned_result.split('. ', 1)[1]
                
                parsed_results.append({
                    'rank': idx,
                    'result': cleaned_result
                })
        
        return parsed_results
    
    except Exception as e:
        st.error(f"Error occurred while searching: {str(e)}")
        return []

def analyze_rankings(results: List[Dict], target_brand: str) -> Dict:
    """Analyze the rankings for mentions of the target brand"""
    analysis = {
        'found': False,
        'rank': None,
        'context': None,
        'total_results': len(results)
    }
    
    if not target_brand or not results:
        return analysis
    
    target_brand = target_brand.lower()
    for result in results:
        if target_brand in result['result'].lower():
            analysis['found'] = True
            analysis['rank'] = result['rank']
            analysis['context'] = result['result']
            break
    
    return analysis

# Main app title
st.title("🔍 Keyword Ranking Analysis Tool")

# Instructions
with st.expander("ℹ️ How to use this tool", expanded=True):
    st.write("""
    **How Users Actually Search in AI Tools:**

    1. Direct Comparisons: 
        "zapier vs make pricing"
        - Short and direct
        - Specific aspect (pricing)
        - No fluff
        
    2. Local Search:
        "best vegan restaurants mumbai"
        - Location + category
        - Simple qualifier
        - No complex phrases

    3. Tool/Product Search:
        "chatgpt alternatives free"
        - Named product
        - Key qualifier (free)
        - Direct intent

    4. Category Lists:
        "top AI image generators 2024"
        - Clear category
        - Timeframe
        - List intent

    5. Problem-Solving:
        "how to embed youtube video wordpress"
        - Task-focused
        - Platform specific
        - No unnecessary words

    6. Reviews/Rankings:
        "best project management tools 2024"
        - Category
        - Timeline
        - Quality indicator
    """)

# API Configuration in sidebar
st.sidebar.title("API Configuration")
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Enter your OpenAI API key"
)

# Initialize OpenAI client when API key is provided
if api_key:
    try:
        # Initialize the OpenAI client with just the API key
        st.session_state.openai_client = OpenAI(api_key=api_key)
        st.sidebar.success("✅ API key configured successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Error initializing OpenAI client: {str(e)}")
        st.session_state.openai_client = None

# Main input fields
target_brand = st.text_input(
    "Your Brand Name",
    help="Enter your brand name exactly as it appears online"
)

keyword = st.text_input(
    "Search Keyword",
    help="Enter a specific keyword to analyze"
)

# Analysis button
if st.button("🔍 Analyze Rankings", type="primary"):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar first.")
    elif not all([keyword, target_brand]):
        st.warning("Please fill in both the brand name and search keyword.")
    elif not validate_keyword(keyword):
        st.warning("""
        ⚠️ Please enter a more specific keyword. Your keyword should:
        - Be at least 3 words long
        - Or include specific comparisons (vs, versus)
        - Or include qualifiers (best, top, free, etc.)
        """)
    else:
        with st.spinner("🔄 Analyzing rankings..."):
            results = search_openai(keyword)
            
            if results:
                analysis = analyze_rankings(results, target_brand)
                
                # Display results
                st.subheader("📊 Search Results")
                df = pd.DataFrame(results)
                st.dataframe(
                    df,
                    column_config={
                        "rank": "Rank",
                        "result": "Result"
                    },
                    hide_index=True
                )
                
                st.subheader("🎯 Brand Analysis")
                if analysis['found']:
                    st.success(f"✨ Your brand was found at rank {analysis['rank']}")
                    st.info("Context:")
                    st.write(analysis['context'])
                else:
                    st.warning("⚠️ Your brand was not found in the top results.")
                    st.write("Recommendations:")
                    st.write("- Optimize your online presence")
                    st.write("- Try different keyword variations")
                    st.write("- Focus on specific geographic/niche markets")
                
                st.metric(
                    label="Total Results Analyzed",
                    value=analysis['total_results']
                )

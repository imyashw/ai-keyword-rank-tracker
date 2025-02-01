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

# Initialize session state for OpenAI client
if 'openai_client' not in st.session_state:
    st.session_state.openai_client = None

def validate_keyword(keyword: str) -> bool:
    """Validate if the keyword is specific enough"""
    if not keyword:
        return False
    words = keyword.lower().split()
    return len(words) >= 4

def initialize_openai_client(api_key: str) -> None:
    """Initialize OpenAI client with API key"""
    try:
        st.session_state.openai_client = OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {str(e)}")
        st.session_state.openai_client = None

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

# Main app
st.title("🔍 Keyword Ranking Analysis Tool")

# Instructions
with st.expander("ℹ️ How to use this tool", expanded=True):
    st.write("""
    This tool analyzes search rankings for specific keywords related to your brand.
    
    **Guidelines for good keywords:**
    1. Be specific and detailed (minimum 4 words)
    2. Include location if relevant
    3. Include specific product/service category
    4. Target your niche market
    
    **Effective Search Patterns for AI Analysis:**

    ✅ Listicle-Style Queries:
    1. "top 10 plus size clothing brands compared to XYZ brand"
       - Requests specific list format
       - Includes direct comparison
       - Clear brand benchmark
       - Defined market segment

    2. "best alternatives to [Your Brand] for organic skincare"
       - Triggers comparison analysis
       - Specifies market niche
       - Focuses on alternatives
       - Natural search pattern

    3. "which brands compete with [Your Brand] in premium handbags"
       - Asks for competitive analysis
       - Defines market segment
       - Price category specified
       - Question format works well with AI

    ✅ Comparison-Focused Queries:
    1. "how does [Your Brand] compare to leading Mumbai fashion brands"
       - Direct comparison request
       - Geographic focus
       - Industry specific
       - Evaluative context

    2. "is [Your Brand] better than [Competitor] for vegan cosmetics"
       - Direct competitor comparison
       - Specific product category
       - Clear evaluation request
       - User-intent focused

    💡 Why These Work Better with AI:
    - Trigger list generation
    - Request direct comparisons
    - Use natural question formats
    - Include brand context
    - Specify market segments
    - Ask for rankings/evaluations
    """)

# Input fields
api_key = st.text_input(
    "OpenAI API Key",
    type="password",
    help="Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys"
)

if api_key and st.session_state.openai_client is None:
    initialize_openai_client(api_key)

target_brand = st.text_input(
    "Your Brand Name",
    help="Enter your brand name exactly as it appears online"
)

keyword = st.text_input(
    "Search Keyword",
    help="Enter a specific keyword to analyze (minimum 4 words)"
)

# Analysis button
if st.button("🔍 Analyze Rankings", type="primary"):
    if not all([api_key, keyword, target_brand]):
        st.warning("Please fill in all fields to proceed.")
    
    elif not validate_keyword(keyword):
        st.warning("""
        ⚠️ Please enter a more specific keyword. Your keyword should:
        - Be at least 4 words long
        - Include specific details (location, category, etc.)
        - Be relevant to your brand
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

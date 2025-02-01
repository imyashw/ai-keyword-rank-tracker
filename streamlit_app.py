import os
import openai
from streamlit import st

# Initialize OpenAI client with API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    # Create a title for the app
    st.title("OpenAI Keyword Research Tool")
    
    # Create an input area for keywords
    keywords_input = st.text_area(
        "Enter Keywords to Search (press Enter or click Clear)",
        value="Type your keywords here..."
    )
    
    # Create buttons: Clear and Search
    clear_button = st.button("Clear Input", key="clear")
    search_button = st.button("Search Keywords", key="search")
    
    if clear_button or keywords_input.strip() == '':
        keywords_input = st.empty()
        return
    
    if search_button:
        try:
            # OpenAI API call
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze the following keyword(s) and provide a brief analysis of where they appear in search results. List URLs in a clear format."
                    }
                ],
                stream=True
            )
            
            # Extract and display results
            st.write("\nResults:")
            if response.choices[0].message.content:
                st.code(response.choices[0].message.content)
            else:
                st.error("No results found.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

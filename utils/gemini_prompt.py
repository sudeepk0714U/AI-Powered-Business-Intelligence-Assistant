import google.generativeai as genai
import pandas as pd

def setup_gemini(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

def generate_response(model, user_query: str, df: pd.DataFrame):
    schema = df.dtypes.to_string()

    prompt = f"""
You are a smart Python data analyst working with this DataFrame (called 'df').

Schema:
{schema}

User's Question:
\"\"\"{user_query}\"\"\"

Respond with:
- ✅ Python Pandas code using 'df' if analysis or chart is needed
- 📝 A short textual summary if a description is enough
- 📊 Use matplotlib if chart is required (do not call plt.show())

Respond with code or markdown, no explanation.
"""
    response = model.generate_content(prompt)
    return response.text.strip()

import os
import re
import io
import contextlib
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.gemini_prompt import setup_gemini, generate_response


api_key = st.secrets["GEMINI_API_KEY"]


model = setup_gemini(api_key)

st.set_page_config(page_title="📊 AI BI Assistant (Gemini Flash)", layout="wide")
st.title("📊 AI-Powered Business Intelligence Assistant (CSV + Gemini Flash)")


if "history" not in st.session_state:
    st.session_state.history = []


uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")
    st.dataframe(df.head())


    user_query = st.text_input("Ask a question about your data:", placeholder="e.g., What was the total revenue by region?")

    if user_query:
        with st.spinner("Thinking with Gemini Flash..."):
            output = generate_response(model, user_query, df)


            st.session_state.history.append({
                "query": user_query,
                "response": output
            })

            code_match = re.search(r"```(?:python)?\n(.*?)```", output, re.DOTALL)

            if code_match:
                code = code_match.group(1).strip()
                st.subheader("📊 Generated Code:")
                st.code(code, language="python")

                try:
                    exec_locals = {"df": df, "plt": plt}

                    stdout_buffer = io.StringIO()
                    with contextlib.redirect_stdout(stdout_buffer):
                        exec(code, {}, exec_locals)


                    stdout_content = stdout_buffer.getvalue().strip()
                    if stdout_content:
                        st.subheader("🖨️ Output:")
                        st.text(stdout_content)


                    for i in plt.get_fignums():
                        fig = plt.figure(i)
                        st.pyplot(fig)
                        plt.close(fig)


                    result = exec_locals.get("result")
                    if isinstance(result, pd.DataFrame):
                        st.dataframe(result)

                except Exception as e:
                    st.error(f"Error executing generated code: {e}")
            else:
                st.subheader("📝 Answer:")
                st.markdown(output)


    with st.sidebar.expander("🕘 Past Queries"):
        for item in reversed(st.session_state.history):
            st.markdown(f"**Q:** {item['query']}")
            st.markdown(f"**A:** {item['response'][:300]}{'...' if len(item['response']) > 300 else ''}")
            st.markdown("---")

else:
    st.info("Please upload a CSV file to begin.")

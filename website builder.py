import streamlit as st
import zipfile
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
load_dotenv()

if "GOOGLE_API_KEY" not in os.environ and "GOOGLE_API_KEY" not in st.secrets:
    st.error("GOOGLE_API_KEY is missing. Add it to Streamlit or Hugging Face secrets.")
    st.stop()

# --------------------------------------------------
# STREAMLIT CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Free AI Website Builder",
    page_icon="🤖",
    layout="centered"
)

st.title("AI Website Builder")

prompt = st.text_area(
    "Describe your website",
    placeholder="Example: A modern portfolio website with hero section, projects, and contact form"
)

# --------------------------------------------------
# GENERATE BUTTON
# --------------------------------------------------
if st.button("Generate Website", type="primary"):

    if not prompt.strip():
        st.warning("Please describe your website.")
        st.stop()

    messages = [
        SystemMessage(content="""
You are a senior frontend engineer.

Generate a modern, premium, responsive frontend website.

Rules (MUST FOLLOW STRICTLY):
- Use semantic HTML5
- Use external CSS
- Use vanilla JavaScript only
- No frameworks or libraries
- Modern UI (gradients, cards, shadows)
- Fully responsive
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include backticks

OUTPUT FORMAT (EXACT):

---html---
[html code]
---html---

---css---
[css code]
---css---

---js---
[js code]
---js---
"""),
        HumanMessage(content=prompt)
    ]

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.6,
        max_output_tokens=8192
    )

    with st.spinner("Generating website..."):
        response = model.invoke(messages)

    content = response.content

    try:
        html = content.split("---html---")[1].split("---html---")[0].strip()
        css  = content.split("---css---")[1].split("---css---")[0].strip()
        js   = content.split("---js---")[1].split("---js---")[0].strip()
    except Exception:
        st.error("Model response format invalid. Click Generate again.")
        st.stop()

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    with open("style.css", "w", encoding="utf-8") as f:
        f.write(css)

    with open("script.js", "w", encoding="utf-8") as f:
        f.write(js)

    with zipfile.ZipFile("website.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("index.html")
        zipf.write("style.css")
        zipf.write("script.js")

    with open("website.zip", "rb") as f:
        st.download_button(
            "Download Website ZIP",
            data=f,
            file_name="website.zip",
            mime="application/zip"
        )

    st.success("Website generated successfully!")


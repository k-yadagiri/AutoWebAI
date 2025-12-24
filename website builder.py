import streamlit as st
import zipfile
import re
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.set_page_config(page_title="Free AI website builder", page_icon="🤖")
st.title("AI website builder")

prompt = st.text_area("Write here about your website")

# --------------------------------------------------
# Helper function for robust parsing
# --------------------------------------------------
def extract_sections(content):
    def block(name):
        match = re.search(
            rf"---{name}---(.*?)---{name}---",
            content,
            re.DOTALL | re.IGNORECASE
        )
        return match.group(1).strip() if match else None

    html = block("html")
    css  = block("css")
    js   = block("js")

    if html and css and js:
        return html, css, js

    raise ValueError("Invalid format")

# --------------------------------------------------
# Generate button
# --------------------------------------------------
if st.button("generate"):

    if not prompt.strip():
        st.warning("Please describe your website.")
        st.stop()

    # ✅ Correct message format for Gemini
    messages = [
        SystemMessage(content="""You are a senior frontend engineer.

Generate a modern, premium, responsive frontend website.

Rules (MUST FOLLOW):
- Use semantic HTML5, external CSS, and vanilla JavaScript.
- Design must be modern and visually rich (gradients, cards, depth).
- Do not use frameworks or libraries.
- Do not include explanations or markdown.

Output MUST be EXACTLY in this format and nothing else:

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

    # ✅ Stable, widely available model
    model = ChatGoogleGenerativeAI(
        model="gemini-pro",
        temperature=0.6,
        max_output_tokens=4096
    )

    with st.spinner("Generating website..."):
        response = model.invoke(messages)

    content = response.content

    # --------------------------------------------------
    # Robust parsing with auto-fix
    # --------------------------------------------------
    try:
        html, css, js = extract_sections(content)

    except ValueError:
        st.warning("Fixing model output format automatically...")

        repair_prompt = f"""
Rewrite the following output EXACTLY in this format and NOTHING else:

---html---
(valid HTML only)
---html---

---css---
(valid CSS only)
---css---

---js---
(valid JavaScript only)
---js---

Original output:
{content}
"""

        repair_messages = [
            SystemMessage(content="Fix formatting only. Do not change content."),
            HumanMessage(content=repair_prompt)
        ]

        repaired = model.invoke(repair_messages).content

        try:
            html, css, js = extract_sections(repaired)
        except ValueError:
            st.error("Model failed to produce valid output. Please try again.")
            st.stop()

    # --------------------------------------------------
    # Write files
    # --------------------------------------------------
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    with open("style.css", "w", encoding="utf-8") as f:
        f.write(css)

    with open("script.js", "w", encoding="utf-8") as f:
        f.write(js)

    # --------------------------------------------------
    # Zip files
    # --------------------------------------------------
    with zipfile.ZipFile("website.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("index.html")
        zipf.write("style.css")
        zipf.write("script.js")

    # --------------------------------------------------
    # Download
    # --------------------------------------------------
    with open("website.zip", "rb") as f:
        st.download_button(
            "Click to download",
            data=f,
            file_name="website.zip",
            mime="application/zip"
        )

    st.success("Website generated successfully")



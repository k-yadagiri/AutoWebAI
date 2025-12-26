import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import zipfile
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(page_title="Free AI website builder",page_icon="🤖")

st.title("AI website builder")

prompt=st.text_area("write here about your website")

if st.button("generate"):
    message=[("system",""" You are a senior frontend engineer.

Generate a modern, premium, responsive frontend website.

STRICT RULES:
- HTML block → ONLY HTML
- CSS block → ONLY CSS
- JS block → ONLY JavaScript
- NEVER repeat block markers
- NEVER nest code between blocks
- Each block must contain only its own language.
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
     
""")]
    
    message.append(("user", prompt))

    model=ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
    response = model.invoke(message)

    content = response.content

    try:
        html = content.split("---html---")[1].split("---html---")[0].strip()
        css  = content.split("---css---")[1].split("---css---")[0].strip()
        js   = content.split("---js---")[1].split("---js---")[0].strip()
    except IndexError:
        st.error("Model output format is invalid. Please try again.")
        st.stop()

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    with open("style.css", "w", encoding="utf-8") as f:
        f.write(css)

    with open("script.js", "w", encoding="utf-8") as f:
        f.write(js)

    with zipfile.ZipFile("website.zip", "w") as zipf:
        zipf.write("index.html")
        zipf.write("style.css")
        zipf.write("script.js")

    


    st.download_button("click to download",
                       data=open("website.zip","rb"),
                       file_name="website.zip")


    st.write("success")

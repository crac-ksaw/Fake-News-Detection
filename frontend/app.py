import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/verify")

st.set_page_config(page_title="Fake News Detector (v2)", layout="centered", page_icon="🧠")
st.markdown("<h1 style='color:#fff'>🧠 Fake News Detector</h1>", unsafe_allow_html=True)
st.markdown("## Enter the news headline or article to verify:")

with st.form(key="headline_form"):
    text = st.text_area("📰 News Content", placeholder="Enter news here...", height=150)
    submitted = st.form_submit_button("🔍 Analyze")

if submitted and text:
    if len(text) < 10:
        st.error("Text is too short. Please provide more context.")
    else:
        with st.spinner("Analyzing via RAG Pipeline..."):
            try:
                response = requests.post(API_URL, json={"text": text}, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    classification = data.get("classification", "UNCERTAIN")
                    confidence = data.get("confidence_score", 0.0)
                    reasoning = data.get("reasoning", "")
                    context = data.get("retrieved_context", [])

                    # UI Logic
                    if classification == "FAKE":
                        st.success(f"❌ FAKE NEWS detected. (Confidence: {confidence:.2f})")
                    elif classification == "REAL":
                        st.success(f"✅ REAL NEWS verified. (Confidence: {confidence:.2f})")
                    else:
                        st.warning(f"⚠️ UNCERTAIN. Could not confidently classify. (Confidence: {confidence:.2f})")

                    st.markdown("### 📘 Reasoning:")
                    st.markdown(reasoning)

                    if context:
                        with st.expander("Show Retrieved Context"):
                            for idx, c in enumerate(context):
                                st.markdown(f"**Context {idx+1}:** {c}")
                else:
                    st.error(f"API Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {e}")

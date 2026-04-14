import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/verify")

st.set_page_config(page_title="Fake News Detector", layout="centered")
st.title("Fake News Detector")
st.markdown("Enter a news headline or article to verify.")

with st.form(key="headline_form"):
    text = st.text_area("News Content", placeholder="Enter news here...", height=150)
    submitted = st.form_submit_button("Analyze")

if submitted and text:
    if len(text) < 10:
        st.error("Text is too short. Please provide more context.")
    else:
        with st.spinner("Analyzing the headline..."):
            try:
                response = requests.post(API_URL, json={"text": text}, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    classification = data.get("classification", "UNCERTAIN")
                    confidence = data.get("confidence_score", 0.0)
                    reasoning = data.get("reasoning", "")

                    if classification == "FAKE":
                        st.error(f"FAKE NEWS detected. (Confidence: {confidence:.2f})")
                    elif classification == "REAL":
                        st.success(f"REAL NEWS verified. (Confidence: {confidence:.2f})")
                    else:
                        st.warning(
                            f"UNCERTAIN. Could not confidently classify. (Confidence: {confidence:.2f})"
                        )

                    st.markdown("### Reasoning")
                    st.markdown(reasoning)
                else:
                    st.error(f"API Error: {response.text}")
            except Exception as exc:
                st.error(f"Failed to connect to API: {exc}")

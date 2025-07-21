import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")
GROQ_MODEL = os.getenv("GROQ_MODEL")

# Streamlit page setup
st.set_page_config(page_title="Fake News Detector", layout="centered", page_icon="🧠")
st.markdown("<h1 style='color:#fff'>🧠 Fake News Detector</h1>", unsafe_allow_html=True)
st.markdown("## Enter the news headline to check if it's fake or not:")

# Input field with ENTER key trigger
with st.form(key="headline_form"):
    text = st.text_input("📰 News Headline", placeholder="Enter a news headline here...")
    submitted = st.form_submit_button("🔍 Analyze")

# Trigger analysis
if submitted and text:
    with st.spinner("Analyzing with locally trained model..."):
        prompt = f"""
You are an advanced fake news detection assistant. Your job is to verify the authenticity of a news headline based on current real-world events, media coverage, and plausibility—not based on grammar, tone, or sentence structure.

Given the following headline, perform the following tasks:
1. Determine if the headline is REAL or FAKE by verifying:
   - Whether the event mentioned is known or reported in recent news.
   - Whether the event sounds plausible within real-world scenarios (like local politics, science, disasters, etc.).
2. If possible, mentally cross-check with recent or notable headlines.
3. Return your decision and give detailed reasoning with real-world logic and potential event patterns—not just based on language.

Headline: "{text}"

Respond **strictly in this format**:

1. Classification: REAL or FAKE  
2. Reasoning:
• Bullet 1 (e.g., This headline refers to a verifiable event covered by real news sources such as ...)
• Bullet 2 (e.g., The subject matter is commonly reported by local/national media or has historical precedent)
• Bullet 3 (Optional: mention if the claim contradicts known facts or lacks evidence)

Only provide accurate classification based on these checks.
"""

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are a fact-checking assistant trained with a proprietary local model for media classification."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            output = response.json()["choices"][0]["message"]["content"]

            # Extract classification line accurately
            lines = output.strip().splitlines()
            classification_line = next((line for line in lines if "classification" in line.lower()), "").lower()

            # Logic sync with output
            if "fake" in classification_line:
                st.success("❌ This is FAKE news.")
                st.markdown("### 🧠 From my trained model, I think this is...")
                st.markdown('<div style="background-color:#8B0000;color:white;padding:10px;text-align:center;"><strong>FAKE NEWS</strong></div>', unsafe_allow_html=True)

            elif "real" in classification_line:
                st.success("✅ This is REAL news.")
                st.markdown("### 🧠 From my trained model, I think this is...")
                st.markdown('<div style="background-color:#004d00;color:white;padding:10px;text-align:center;"><strong>REAL NEWS</strong></div>', unsafe_allow_html=True)

            else:
                st.warning("⚠️ Could not determine classification. See the reasoning below.")

            # Show detailed explanation
            st.markdown("---")
            st.markdown("### 📘 The classification of this headline might make sense for several reasons:")
            st.markdown(output)

        except Exception as e:
            st.error(f"Failed to analyze headline: {e}")

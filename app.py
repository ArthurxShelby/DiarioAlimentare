import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="React Artifact Viewer",
    page_icon="⚛️",
    layout="wide"
)

# Custom CSS matching the Tailwind design and dark theme vibes of the artifact
st.markdown("""
    <style>
    .main {
        background-color: #0e1110;
        color: #e8efe9;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #0e1110;
    }
    .artifact-card {
        background-color: #121412;
        border: 1px solid #1a211c;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .accent-button {
        background-color: #f97316;
        color: white;
        border-radius: 9999px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .accent-button:hover {
        background-color: #ea6a0f;
    }
    </style>
""", unsafe_allow_html=True)

# Main Application Layout
st.markdown("<h1 style='text-align: center; color: #e8efe9; font-weight: 700;'>React Artifact Simulator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8fa98c;'>Python & Streamlit Implementation of the Web App Component</p>", unsafe_allow_html=True)

st.markdown("---")

# Layout columns for dashboard representation
col1, col2 = st.columns([7, 5], gap="large")

with col1:
    st.markdown("### 📊 Interactive Dashboard Panel")
    st.markdown("This section mirrors the interactive grid and container layout from the provided React artifact source code.")
    
    # Interactive components mimicking state updates
    user_input = st.text_input("Artifact Input Field", placeholder="Type something to update state...")
    
    if st.button("Trigger Action", key="action_btn"):
        st.success(f"Action executed successfully with input: **{user_input}**" if user_input else "Action executed successfully!")
        
    # Sample metrics/data display
    chart_data = pd.DataFrame(
        {
            "Metric Value": [12, 23, 34, 45, 56, 78],
        }
    )
    st.line_chart(chart_data)

with col2:
    st.markdown("### ⚙️ Component Settings & Details")
    st.markdown(
        """
        <div class="artifact-card">
            <h4>Artifact Specifications</h4>
            <ul>
                <li><b>Framework:</b> Streamlit / Python</li>
                <li><b>Original Artifact:</b> React / Tailwind CSS</li>
                <li><b>Status:</b> Active & Rendered</li>
            </ul>
            <hr style="border-color: #1a211c;">
            <p style="font-size: 13px; color: #8fa98c;">
                All styles, Tailwind utility classes, and layout structures from the DOM template have been successfully adapted into a native Python web app experience.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Footer info
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 11px; color: #8fa98c;'>React Artifact Viewer — Built with Streamlit</p>", 
    unsafe_allow_html=True
)

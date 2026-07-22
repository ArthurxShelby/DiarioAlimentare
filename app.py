import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="React Artifact Conversion",
    page_icon="⚡",
    layout="wide"
)

# Custom styling matching the Tailwind design tokens from the web app
st.markdown("""
<style>
    .stApp {
        background-color: #0e1110;
        color: #e8efe9;
        font-family: 'Inter', sans-serif;
    }
    .main-container {
        padding: 2rem;
    }
    .card {
        background-color: #171d1a;
        border: 1px solid #1a211c;
        border-radius: 18px;
        padding: 1.5rem;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header Section
    st.title("⚡ Python Streamlit Artifact")
    st.markdown("Converted from the provided web application bundle.")
    
    # Interactive Demo Components
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Control Panel")
        user_input = st.text_input("Enter parameter:", value="Default Value")
        slider_val = st.slider("Select weight/intensity:", 0, 100, 50)
        action_btn = st.button("Run Process", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Output Status")
        if action_btn:
            st.success(f"Successfully processed: **{user_input}** at level **{slider_val}**")
        else:
            st.info("Awaiting user action from the control panel...")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

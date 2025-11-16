"""
AIATL - AI-Assisted Triage and Learning System
Main Streamlit Application Entry Point
"""

import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pages import home, login, register, patient_dashboard, doctor_dashboard

def main():
    """Main application entry point with page routing"""
    st.set_page_config(
        page_title="AIATL - Healthcare Management System",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar navigation
    st.sidebar.title("AIATL Healthcare System")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Navigate to:",
        [
            "Home",
            "Login",
            "Register",
            "Patient Dashboard",
            "Doctor Dashboard"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Show login status
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.sidebar.success(f"Logged in as: {st.session_state.get('username', 'Unknown')}")
        st.sidebar.write(f"Role: {st.session_state.get('role', 'Unknown').title()}")
        if st.sidebar.button("Logout", key="sidebar_logout"):
            st.session_state.clear()
            st.rerun()
    else:
        st.sidebar.info("Please log in to access patient/doctor features")
    
    # Route to appropriate page
    if page == "Home":
        home.main()
    elif page == "Login":
        login.main()
    elif page == "Register":
        register.main()
    elif page == "Patient Dashboard":
        patient_dashboard.main()
    elif page == "Doctor Dashboard":
        doctor_dashboard.main()

if __name__ == "__main__":
    main()

import streamlit as st
from app.utils.helpers import (
    load_css,
    display_header,
    get_current_timestamp,
    get_mongo_client,
)
import json
from datetime import datetime
import warnings
import logging

# Suppress PyTorch warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", message=".*torch.classes.*")
logging.getLogger("torch").setLevel(logging.ERROR)

from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import numpy as np
from ai_crew.main import run




def main():
    load_css("app/static/css/styles.css")
    display_header()

    st.markdown("---")
    st.header("Patients Page")

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if st.session_state["role"] == "patient":
            st.write("""
                Welcome to the **Patients Dashboard**. You can input your symptoms below to help healthcare providers understand your condition.
            """)

            with st.form("patient_dashboard_symptom_form"):
                symptoms = st.text_area("Describe your symptoms here:", height=200)
                submit = st.form_submit_button("Submit Symptoms")

            if submit:
                if symptoms.strip() == "":
                    st.error("Please enter your symptoms before submitting.")
                else:
                    symptom_data = {
                        "username": st.session_state["username"],
                        "symptoms_text": symptoms.strip(),
                        "submitted_at": get_current_timestamp(),
                    }

                    client = get_mongo_client()
                    if client:
                        db = client["myDatabase"]
                        symptoms_collection = db["symptoms"]
                        user_collection = db["users"]

                        def get_user_profile(username):
                            return user_collection.find_one({"username": username})
                        user_profile = get_user_profile(st.session_state["username"])

                        try:
                            symptoms_collection.insert_one(symptom_data)
                            st.success(
                                "Your symptoms have been successfully submitted!"
                            )
                            
                            # Run AI crew analysis
                            with st.spinner("AI doctors are analyzing your symptoms..."):
                                try:
                                    st.write("Starting AI analysis...")
                                    # Run analysis and store results in MongoDB
                                    run(
                                        symptoms.strip(), 
                                        user_profile.get("name", "Name not specified"), 
                                        user_profile.get("ethnicity", "Ethnicity not defined"), 
                                        user_profile.get("sex", "Sex is not defined"),
                                        username=st.session_state["username"]
                                    )
                                    
                                    # Check if analysis was stored in MongoDB
                                    analysis_collection = db["analysis_results"]
                                    latest_analysis = analysis_collection.find_one(
                                        {"username": st.session_state["username"]},
                                        sort=[("created_at", -1)]  # Get most recent
                                    )
                                    
                                    if latest_analysis and latest_analysis.get("final_report"):
                                        st.success("AI analysis complete! Check the results below.")
                                    else:
                                        st.warning("AI analysis completed but no results were generated.")
                                        
                                except Exception as e:
                                    st.error(f"AI analysis failed: {e}")
                                    import traceback
                                    st.error(f"Full error: {traceback.format_exc()}")
                                    return
                            
                            st.rerun()  # Refresh the page to show the new results
                            
                        except Exception as e:
                            st.error(
                                f"An error occurred while submitting your symptoms: {e}"
                            )
                    else:
                        st.error(
                            "Failed to connect to the database. Please try again later."
                        )

                        
        else:
            st.error("Access Denied: You do not have permission to view this page.")
    else:
        st.warning("Please log in to access the Patients page.")
    # Display AI analysis results
    st.markdown("---")
    st.subheader("AI Doctor Analysis Results")

    try:
        # Get analysis results from MongoDB
        client = get_mongo_client()
        if client:
            db = client["myDatabase"]
            analysis_collection = db["analysis_results"]
            
            # Get the most recent analysis for the logged-in user
            if "logged_in" in st.session_state and st.session_state["logged_in"]:
                latest_analysis = analysis_collection.find_one(
                    {"username": st.session_state["username"]},
                    sort=[("created_at", -1)]  # Get most recent
                )
                
                if latest_analysis and latest_analysis.get("final_report"):
                    content = latest_analysis["final_report"]
                    st.text_area("Doctor Recommendation and Potential Diagnoses", content, height=300)
                else:
                    st.info("No analysis results yet. Submit your symptoms above to get AI doctor recommendations.")
            else:
                st.info("Please log in to view your analysis results.")
        else:
            st.error("Failed to connect to the database. Please try again later.")
            
    except Exception as e:
        st.error(f"An error occurred while reading the analysis: {e}")
        st.info("Submit your symptoms above to get AI doctor recommendations.")

if __name__ == "__main__":
    main()

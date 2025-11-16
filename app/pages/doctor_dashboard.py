import streamlit as st
from app.utils.helpers import load_css, display_header, get_mongo_client, get_doctor_specialty, get_username_by_full_name

def main():
    load_css("app/static/css/styles.css")
    display_header()

    st.markdown("---")
    st.header("Doctor's Dashboard")

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if st.session_state["role"] == "doctor":
            st.write(
               "Welcome, Doctor! Use the search bar below to view a patient's symptoms."
           )

            with st.form("doctor_dashboard_search_form"):
               username = st.text_input("Enter the patient's username:")
               submit = st.form_submit_button("Search")

            if submit:
                if username.strip() == "":
                   st.error("Please enter a username to search.")
                else:
                    client = get_mongo_client()
                    if client:
                        db = client["myDatabase"]
                        symptoms_collection = db["symptoms"]

                        symptoms = list(
                            symptoms_collection.find({"username": username})
                       )

                        if symptoms:
                            st.success(
                               f"Found {len(symptoms)} symptoms for user: {username}"
                           )
                            for i, symptom in enumerate(symptoms, start=1):
                               st.markdown(f"### Symptom #{i}")
                               st.write(f"**Symptoms:** {symptom['symptoms_text']}")
                               st.markdown("---")
                        else:
                           st.warning(
                               f"No symptoms found for the username: {username}"
                           )
                    else:
                        st.error(
                           "Failed to connect to the database. Please try again later."
                       )
            st.markdown("---")
            st.subheader("Alerts")
            doctor_username = st.session_state.get('username', None)
            doctor_specialty = get_doctor_specialty(doctor_username)
            
            # Get the most recent analysis from MongoDB
            client = get_mongo_client()
            if client:
                db = client["myDatabase"]
                analysis_collection = db["analysis_results"]
                
                # Get the most recent analysis
                latest_analysis = analysis_collection.find_one(
                    sort=[("created_at", -1)]  # Get most recent
                )
                
                if not latest_analysis:
                    st.info("No analysis reports found.")
                else:
                    try:
                        report_content = latest_analysis.get("final_report", "")
                        
                        if not report_content:
                            st.info("Report is empty.")
                        else:
                            # Parse the report to extract specialty and patient info
                            # The report format appears to be: "Specialty PatientName, Report body..."
                            words = report_content.split()
                            if len(words) >= 2:
                                # Extract specialty and patient name
                                report_specialty = words[0]
                                patient_full_name = words[1].replace(",", "")
                                report_body = ' '.join(words[2:]) if len(words) > 2 else ""
                                
                                # Compare report specialty with doctor's specialty (case-insensitive)
                                # Remove any trailing punctuation from report_specialty
                                report_specialty_clean = report_specialty.rstrip('.,!?').lower()
                                doctor_specialty_clean = doctor_specialty.lower() if doctor_specialty else ""
                                
                                if report_specialty_clean == doctor_specialty_clean:
                                    # Display the alert
                                    st.write(f"**Patient Name:** {patient_full_name}")
                                    st.write("**Report Content:**")
                                    st.write(report_body if report_body else report_content)
                                else:
                                    st.info("No alerts for your specialty at this time.")
                            else:
                                # If format doesn't match expected, show the full report
                                st.write("**Latest Report:**")
                                st.write(report_content)
                                
                    except Exception as e:
                        st.error(f"An error occurred while processing the report: {e}")
            else:
                st.error("Failed to connect to the database. Please try again later.")

        else:
            st.error("Access Denied: You do not have permission to view this page.")
    else:
        st.warning("Please log in to access the Doctor's Dashboard.")

if __name__ == "__main__":
    main()
import streamlit as st
from app.utils.helpers import load_css, display_header, get_mongo_client, get_doctor_specialty, get_username_by_full_name
import os

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
            doctor_username=st.session_state.get('username', None)
            doctor_specialty=get_doctor_specialty(doctor_username)
            # Path to the report.txt file
            report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "analysis_outputs", "final_report.txt")

                # Check if the report file exists
            if not os.path.exists(report_path):
                st.warning("No report file found.")
            else:
                try:
                    with open(report_path, "r") as file:
                        report_content = file.read().strip()

                    if not report_content:
                        st.info("Report file is empty.")
                    else:
                        # Split the report content into words
                        words = report_content.split()
                        # Extract specialty and patient name
                        report_specialty = words[0]
                        patient_full_name = words[1].replace(",", "")
                        report_body = words[2][0].upper() + words[2][1:]+ " " + ' '.join(words[3:])  # Rest of the report

                            # Compare report specialty with doctor's specialty (case-insensitive)
                        if report_specialty.lower() == doctor_specialty.lower() + ".":
                            # Fetch username based on patient's full name
                                # Display the alert
                                st.write(f"**Patient Name:** {patient_full_name}")
                                st.write("**Report Content:**")
                                st.write(report_body)
                        else:
                            st.info("No alerts for your specialty at this time.")

                except Exception as e:
                    st.error(f"An error occurred while processing the report: {e}")

        else:
            st.error("Access Denied: You do not have permission to view this page.")
    else:
        st.warning("Please log in to access the Doctor's Dashboard.")

if __name__ == "__main__":
    main()
# pages/2_Register.py

import streamlit as st
from app.utils.helpers import (
    load_css,
    display_header,
    get_mongo_client,
    get_current_timestamp,
)
from werkzeug.security import generate_password_hash
from pymongo.errors import DuplicateKeyError

# List of valid doctor PINs
DOCTOR_PINS = ["Doctor1"]

# List of ethnicity options
ETHNICITIES = [
    "African American/Black",
    "Asian/Pacific Islander",
    "Caucasian/White",
    "Hispanic/Latino",
    "Native American/Alaskan Native",
    "Middle Eastern/North African",
    "Other",
    "Prefer not to say",
]
DOCTOR_TYPES = ["Cardiologist", "Neurologist", "Pulmonologist"]


def main():
    load_css("app/static/css/styles.css")
    display_header()

    st.markdown("---")
    st.header("Register")
    st.write("Create a new account by filling in the form below.")

    # Registration Form
    with st.form("register_page_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        username = st.text_input("Username")
        sex = st.selectbox("Select your sex:", ["Male", "Female", "Other"])
        age = st.number_input("Enter your age", min_value=0, max_value=120, step=1)
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Patient", "Doctor"])
        ethnicity = st.selectbox("Select your ethnicity:", ETHNICITIES)

        # Conditionally display Doctor PIN field if "Doctor" is selected
        doctor_pin = None
        if role == "Doctor":
            doctor_pin = st.text_input("Doctor PIN", type="password")
            doctor_speciality = st.selectbox("Select your specialty:", DOCTOR_TYPES)

        submit = st.form_submit_button("Register")

    if submit:
        # Basic form validation
        if not name or not email or not phone or not username or not password:
            st.error("Please fill out all required fields.")

        elif role == "Doctor" and doctor_pin not in DOCTOR_PINS:
            st.error("Invalid Doctor PIN. Please try again.")

        else:
            # Hash the password
            hashed_password = generate_password_hash(password)

            if role == "Doctor":
                user = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "username": username,
                    "password": hashed_password,
                    "role": role.lower(),  # Store role in lowercase for consistency
                    "ethnicity": ethnicity,
                    "sex": sex,
                    "age": age,
                    "created_at": get_current_timestamp(),
                    "speciality": doctor_speciality,
                }
            elif role == "Patient":
                user = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "username": username,
                    "password": hashed_password,
                    "role": role.lower(),  # Store role in lowercase for consistency
                    "ethnicity": ethnicity,
                    "sex": sex,
                    "age": age,
                    "created_at": get_current_timestamp(),
                }
            else:
                print("Uh oh")

            # Connect to MongoDB
            client = get_mongo_client()
            if client:
                db = client["myDatabase"]  # Replace with your DB name
                users_collection = db["users"]

                # Ensure unique username and email
                try:
                    users_collection.create_index("username", unique=True)
                    users_collection.create_index("email", unique=True)

                    # Insert the user document
                    users_collection.insert_one(user)
                    st.success("Registration successful! You can now log in.")
                    st.balloons()
                except DuplicateKeyError as e:
                    if "username" in str(e):
                        st.error(
                            "Username already exists. Please choose a different one."
                        )
                    elif "email" in str(e):
                        st.error("An account with this email already exists.")
                except Exception as e:
                    st.error(f"An error occurred during registration: {e}")
            else:
                st.error("Failed to connect to the database. Please try again later.")


if __name__ == "__main__":
    main()

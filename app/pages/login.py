import streamlit as st
from app.utils.helpers import load_css, display_header, get_mongo_client
from werkzeug.security import check_password_hash
from pymongo.errors import PyMongoError


def main():
    load_css("app/static/css/styles.css")
    display_header()

    st.markdown("---")
    st.header("Login")
    st.write("Access your account by entering your credentials below.")

    with st.form("login_page_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            client = get_mongo_client()
            if client:
                db = client["myDatabase"]
                users_collection = db["users"]

                try:
                    user = users_collection.find_one({"username": username})
                    if user and check_password_hash(user["password"], password):
                        st.success(f"Welcome back, {user['name']}!")
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.session_state["role"] = user["role"]
                        st.rerun()
                        if user["role"]=="doctor":
                            speciality=user.get('speciality', None)
                            if speciality:
                                st.session_state['speciality']==speciality
                            else:
                                st.warning("Doctor's speciality not found")
                    else:
                        st.error("Invalid username or password.")
                except PyMongoError as e:
                    st.error(f"An error occurred while accessing the database: {e}")
            else:
                st.error("Failed to connect to the database. Please try again later.")

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.write(
            f"Logged in as **{st.session_state['username']}** ({st.session_state['role'].capitalize()})"
        )
        if st.button("Logout", key="login_page_logout"):
            st.session_state.clear()
            st.success("You have been logged out.")
            st.rerun()


if __name__ == "__main__":
    main()

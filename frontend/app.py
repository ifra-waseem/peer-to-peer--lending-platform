import streamlit as st
import requests

BACKEND_URL = "http://backend:8000"  # Update this if your backend runs on a different URL

def main():
    st.title("Peer-to-Peer Lending Platform")

    menu = [
        "User Operations",
        "Lender Operations", 
        "Loan Operations",
        "View All Data"
    ]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "User Operations":
        user_operations()

    elif choice == "Lender Operations":
        lender_operations()

    elif choice == "Loan Operations":
        loan_operations()

    elif choice == "View All Data":
        view_all_data()

def user_operations():
    st.header("User Operations")
    user_choice = st.selectbox(
        "Select Operation",
        ["Register User", "View User", "Update User", "Delete User"]
    )

    if user_choice == "Register User":
        with st.form("user_form"):
            user_id = st.number_input("User ID", min_value=1)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            if st.form_submit_button("Register"):
                response = requests.post(
                    f"{BACKEND_URL}/users/",
                    json={
                        "username": username,
                        "password": password,
                        "email": email,
                        "phone_number": phone
                    }
                )
                if response.status_code == 200:
                    st.success("User registered successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Registration failed: {response.text}")

    elif user_choice == "View User":
        user_id = st.number_input("Enter User ID", min_value=1)
        if st.button("View User"):
            response = requests.get(f"{BACKEND_URL}/users/{user_id}")
            if response.status_code == 200:
                st.json(response.json())
            else:
                st.error(f"Failed to fetch user: {response.text}")

    elif user_choice == "Update User":
        user_id = st.number_input("Enter User ID to Update", min_value=1)
        
        # First fetch existing user data
        if st.button("Load User Data"):
            response = requests.get(f"{BACKEND_URL}/users/{user_id}")
            if response.status_code == 200:
                user_data = response.json()
                st.session_state.user_data = user_data
                st.success("User data loaded!")
            else:
                st.error(f"Failed to load user: {response.text}")
        
        if 'user_data' in st.session_state:
            with st.form("update_user_form"):
                username = st.text_input("Username", value=st.session_state.user_data.get('username', ''))
                email = st.text_input("Email", value=st.session_state.user_data.get('email', ''))
                phone = st.text_input("Phone Number", value=st.session_state.user_data.get('phone_number', ''))
                
                if st.form_submit_button("Update User"):
                    update_data = {
                        "username": username,
                        "email": email,
                        "phone_number": phone
                    }
                    
                    response = requests.put(
                        f"{BACKEND_URL}/users/{user_id}",
                        json=update_data
                    )
                    if response.status_code == 200:
                        st.success("User updated successfully!")
                        st.json(response.json())
                        del st.session_state.user_data  # Clear cached data
                    else:
                        st.error(f"Update failed: {response.text}")

    elif user_choice == "Delete User":
        user_id = st.number_input("Enter User ID to Delete", min_value=1)
        if st.button("Delete User"):
            response = requests.delete(f"{BACKEND_URL}/users/{user_id}")
            if response.status_code == 200:
                st.success("User deleted successfully!")
            else:
                st.error(f"Deletion failed: {response.text}")

def lender_operations():
    st.header("Lender Operations")
    lender_choice = st.selectbox(
        "Select Operation",
        ["Register Lender", "View Lender", "Update Lender", "Delete Lender"]
    )

    if lender_choice == "Register Lender":
        with st.form("lender_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            credit_score = st.number_input("Credit Score", min_value=0.0, max_value=1000.0)
            available_funds = st.number_input("Available Funds", min_value=0.0)
            if st.form_submit_button("Register"):
                response = requests.post(
                    f"{BACKEND_URL}/lenders/",
                    json={
                        "name": name,
                        "email": email,
                        "credit_score": credit_score,
                        "available_funds": available_funds
                    }
                )
                if response.status_code == 200:
                    st.success("Lender registered successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Registration failed: {response.text}")

    elif lender_choice == "View Lender":
        lender_id = st.number_input("Enter Lender ID", min_value=1)
        if st.button("View Lender"):
            response = requests.get(f"{BACKEND_URL}/lenders/{lender_id}")
            if response.status_code == 200:
                st.json(response.json())
            else:
                st.error(f"Failed to fetch lender: {response.text}")

    elif lender_choice == "Update Lender":
        lender_id = st.number_input("Enter Lender ID to Update", min_value=1)
        
        if st.button("Load Lender Data"):
            response = requests.get(f"{BACKEND_URL}/lenders/{lender_id}")
            if response.status_code == 200:
                lender_data = response.json()
                st.session_state.lender_data = lender_data
                st.success("Lender data loaded!")
            else:
                st.error(f"Failed to load lender: {response.text}")
        
        if 'lender_data' in st.session_state:
            with st.form("update_lender_form"):
                name = st.text_input("Name", value=st.session_state.lender_data.get('name', ''))
                email = st.text_input("Email", value=st.session_state.lender_data.get('email', ''))
                credit_score = st.number_input("Credit Score", min_value=0.0, max_value=1000.0, 
                                            value=float(st.session_state.lender_data.get('credit_score', 0)))
                available_funds = st.number_input("Available Funds", min_value=0.0, 
                                                value=float(st.session_state.lender_data.get('available_funds', 0)))
                
                if st.form_submit_button("Update Lender"):
                    update_data = {
                        "name": name,
                        "email": email,
                        "credit_score": credit_score,
                        "available_funds": available_funds
                    }
                    
                    response = requests.put(
                        f"{BACKEND_URL}/lenders/{lender_id}",
                        json=update_data
                    )
                    if response.status_code == 200:
                        st.success("Lender updated successfully!")
                        st.json(response.json())
                        del st.session_state.lender_data
                    else:
                        st.error(f"Update failed: {response.text}")

    elif lender_choice == "Delete Lender":
        lender_id = st.number_input("Enter Lender ID to Delete", min_value=1)
        if st.button("Delete Lender"):
            response = requests.delete(f"{BACKEND_URL}/lenders/{lender_id}")
            if response.status_code == 200:
                st.success("Lender deleted successfully!")
            else:
                st.error(f"Deletion failed: {response.text}")

def loan_operations():
    st.header("Loan Operations")
    loan_choice = st.selectbox(
        "Select Operation",
        ["Create Loan", "View Loan", "Update Loan", "Delete Loan", "Approve Loan"]
    )

    if loan_choice == "Create Loan":
        with st.form("loan_form"):
            borrower_id = st.number_input("Borrower ID", min_value=1)
            lender_id = st.number_input("Lender ID", min_value=1)
            amount = st.number_input("Amount", min_value=0.0)
            interest_rate = st.number_input("Interest Rate (%)", min_value=1.0, max_value=30.0)
            term_months = st.number_input("Term (months)", min_value=1)
            purpose = st.text_input("Purpose")
            if st.form_submit_button("Create"):
                response = requests.post(
                    f"{BACKEND_URL}/loans/",
                    json={
                        "borrower_id": borrower_id,
                        "lender_id": lender_id,
                        "amount": amount,
                        "interest_rate": interest_rate,
                        "term_months": term_months,
                        "purpose": purpose,
                        "status": "pending"
                    }
                )
                if response.status_code == 200:
                    st.success("Loan created successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Loan creation failed: {response.text}")

    elif loan_choice == "View Loan":
        loan_id = st.number_input("Enter Loan ID", min_value=1)
        if st.button("View Loan"):
            response = requests.get(f"{BACKEND_URL}/loans/{loan_id}")
            if response.status_code == 200:
                st.json(response.json())
            else:
                st.error(f"Failed to fetch loan: {response.text}")

    elif loan_choice == "Update Loan":
        loan_id = st.number_input("Enter Loan ID to Update", min_value=1)
        
        if st.button("Load Loan Data"):
            response = requests.get(f"{BACKEND_URL}/loans/{loan_id}")
            if response.status_code == 200:
                loan_data = response.json()
                st.session_state.loan_data = loan_data
                st.success("Loan data loaded!")
            else:
                st.error(f"Failed to load loan: {response.text}")
        
        if 'loan_data' in st.session_state:
            with st.form("update_loan_form"):
                borrower_id = st.number_input("Borrower ID", min_value=1, 
                                           value=st.session_state.loan_data.get('borrower_id', 1))
                lender_id = st.number_input("Lender ID", min_value=1, 
                                          value=st.session_state.loan_data.get('lender_id', 1))
                amount = st.number_input("Amount", min_value=0.0, 
                                       value=float(st.session_state.loan_data.get('amount', 0)))
                interest_rate = st.number_input("Interest Rate (%)", min_value=1.0, max_value=30.0,
                                             value=float(st.session_state.loan_data.get('interest_rate', 5.0)))
                term_months = st.number_input("Term (months)", min_value=1,
                                           value=st.session_state.loan_data.get('term_months', 12))
                purpose = st.text_input("Purpose", 
                                      value=st.session_state.loan_data.get('purpose', ''))
                status = st.selectbox("Status", ["pending", "approved", "rejected", "paid"],
                                    index=["pending", "approved", "rejected", "paid"].index(
                                        st.session_state.loan_data.get('status', 'pending')))
                
                if st.form_submit_button("Update Loan"):
                    update_data = {
                        "borrower_id": borrower_id,
                        "lender_id": lender_id,
                        "amount": amount,
                        "interest_rate": interest_rate,
                        "term_months": term_months,
                        "purpose": purpose,
                        "status": status
                    }
                    
                    response = requests.put(
                        f"{BACKEND_URL}/loans/{loan_id}",
                        json=update_data
                    )
                    if response.status_code == 200:
                        st.success("Loan updated successfully!")
                        st.json(response.json())
                        del st.session_state.loan_data
                    else:
                        st.error(f"Update failed: {response.text}")

    elif loan_choice == "Delete Loan":
        loan_id = st.number_input("Enter Loan ID to Delete", min_value=1)
        if st.button("Delete Loan"):
            response = requests.delete(f"{BACKEND_URL}/loans/{loan_id}")
            if response.status_code == 200:
                st.success("Loan deleted successfully!")
            else:
                st.error(f"Deletion failed: {response.text}")

    elif loan_choice == "Approve Loan":
        loan_id = st.number_input("Enter Loan ID to Approve", min_value=1)
        if st.button("Approve Loan"):
            response = requests.put(
                f"{BACKEND_URL}/loans/{loan_id}/approve"
            )
            if response.status_code == 200:
                st.success("Loan approved successfully!")
                st.json(response.json())
            else:
                st.error(f"Approval failed: {response.text}")

def view_all_data():
    st.header("View All Data")
    
    if st.button("View All Users"):
        response = requests.get(f"{BACKEND_URL}/users/")
        if response.status_code == 200:
            st.subheader("All Users")
            st.write(response.json())
        else:
            st.error(f"Failed to fetch users: {response.text}")

    if st.button("View All Lenders"):
        response = requests.get(f"{BACKEND_URL}/lenders/")
        if response.status_code == 200:
            st.subheader("All Lenders")
            st.write(response.json())
        else:
            st.error(f"Failed to fetch lenders: {response.text}")

    if st.button("View All Loans"):
        response = requests.get(f"{BACKEND_URL}/loans/")
        if response.status_code == 200:
            st.subheader("All Loans")
            st.write(response.json())
        else:
            st.error(f"Failed to fetch loans: {response.text}")

if __name__ == "__main__":
    main()
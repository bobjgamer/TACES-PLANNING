import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import bcrypt
from tax_engine import optimize_family_taxes, analyze_rrsp_scenario
from excel_export import generate_excel_model

st.set_page_config(page_title="Family Tax Planner", layout="wide")

# Dynamically hash the password to guarantee it works flawlessly
hashed_password = bcrypt.hashpw("brrtaces2026".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

credentials = {
    "usernames": {
        "brrtaces": {
            "email": "brrtaces@local.com",
            "name": "Brr Taces",
            "password": hashed_password
        }
    }
}

# Initialize Authenticator for v0.4.x
authenticator = stauth.Authenticate(
    credentials,
    "tax_planner_cookie", 
    "cookie_signature_key", 
    30
)

# In v0.4.x, login() returns None and relies on session_state
authenticator.login(location="main")

auth_status = st.session_state.get("authentication_status")

if auth_status:
    authenticator.logout(location="sidebar")
    
    page = st.sidebar.radio("Navigation", [
        "Dashboard", "Family Inputs", "Registered Accounts", "Scenarios", "Export Model"
    ])
    
    # Session State Initialization
    if 'data' not in st.session_state:
        st.session_state.data = {
            's1_inc': 120000.0, 's1_rrsp': 10000.0, 's1_withheld': 30000.0,
            's2_inc': 80000.0, 's2_rrsp': 5000.0, 's2_withheld': 15000.0,
            'med': 3500.0, 'cc': 6000.0, 'c2_dtc': True
        }

    d = st.session_state.data

    if page == "Dashboard":
        st.title("Family Tax Dashboard (Saskatchewan)")
        
        # Calculate live totals
        res = optimize_family_taxes(d['s1_inc'], d['s1_rrsp'], d['s1_withheld'], d['s2_inc'], d['s2_rrsp'], d['s2_withheld'], d['med'], d['cc'], d['c2_dtc'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Estimated Family Tax", f"${res['total_tax']:,.0f}")
        col2.metric("Estimated Refund / (Owing)", f"${res['total_refund']:,.0f}", 
                    delta="Refund" if res['total_refund'] > 0 else "Owing", 
                    delta_color="normal" if res['total_refund'] > 0 else "inverse")
        col3.metric("Optimized Medical/Childcare", "Applied to S2", "Tax Saver")
        
        st.markdown("### 💡 Top Tax Opportunities")
        
        # Dynamic RRSP Opportunity
        s1_10k_savings = analyze_rrsp_scenario(d['s1_inc'], d['s1_rrsp'], d['s2_inc'], d['s2_rrsp'], 10000, True)
        st.info(f"**Spouse 1 RRSP:** Contributing an additional **$10,000** will generate **${s1_10k_savings:,.0f}** in immediate tax savings.")
        
        # DTC / Childcare Opportunity
        st.success("**DTC Approved (11-yr-old):** System is maximizing the $11,000 childcare limit and transferring DTC credits automatically.")
        
        # RESP Warning
        st.warning("**16-Year-Old RESP Alert:** Age 17 is the final year for CESG. Ensure you contribute $2,500 this year to capture the $500 grant.")

    elif page == "Family Inputs":
        st.title("Income & Deductions")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Spouse 1 (Higher Income)")
            d['s1_inc'] = st.number_input("Employment Income (S1)", value=d['s1_inc'])
            d['s1_withheld'] = st.number_input("Taxes Withheld (S1)", value=d['s1_withheld'])
            d['s1_rrsp'] = st.number_input("RRSP Deductions (S1)", value=d['s1_rrsp'])
        with c2:
            st.subheader("Spouse 2")
            d['s2_inc'] = st.number_input("Employment Income (S2)", value=d['s2_inc'])
            d['s2_withheld'] = st.number_input("Taxes Withheld (S2)", value=d['s2_withheld'])
            d['s2_rrsp'] = st.number_input("RRSP Deductions (S2)", value=d['s2_rrsp'])
            
        st.subheader("Family Expenses")
        d['med'] = st.number_input("Total Medical Expenses", value=d['med'])
        d['cc'] = st.number_input("Total Childcare Expenses", value=d['cc'])
        d['c2_dtc'] = st.checkbox("Child 2 DTC Approved (Valid to 2033)", value=d['c2_dtc'])

    elif page == "Registered Accounts":
        st.title("Registered Accounts Optimizer")
        st.markdown("Track contribution room and optimize asset location.")
        
        tabs = st.tabs(["RRSP", "TFSA", "RESP", "RDSP"])
        with tabs[0]:
            st.write("Spouse 1 Room: $25,000 | Spouse 2 Room: $12,000")
            st.write("*Note: Modeling suggests prioritizing S1 RRSP due to higher marginal rate.*")
        with tabs[2]:
            st.write("### Child 1 (16 yrs old) - URGENT")
            st.error("CESG Eligibility ends at 17. Requires minimum historic contributions or $2,500 this year to qualify.")
        with tabs[3]:
            st.write("### Child 2 (11 yrs old) - RDSP")
            st.success("Because of DTC approval, ensure an RDSP is open to capture up to $3,500/yr in Canada Disability Savings Grants (CDSG).")

    elif page == "Scenarios":
        st.title("Compare Tax Scenarios")
        
        st.write("Compare the baseline against different contribution strategies.")
        additional_rrsp = st.slider("Additional RRSP Contribution to Model", 0, 30000, 10000, 1000)
        
        savings_s1 = analyze_rrsp_scenario(d['s1_inc'], d['s1_rrsp'], d['s2_inc'], d['s2_rrsp'], additional_rrsp, True)
        savings_s2 = analyze_rrsp_scenario(d['s1_inc'], d['s1_rrsp'], d['s2_inc'], d['s2_rrsp'], additional_rrsp, False)
        
        st.bar_chart({"Spouse 1 Contribution": savings_s1, "Spouse 2 Contribution": savings_s2})
        st.write(f"Applying **${additional_rrsp:,.0f}** to Spouse 1 yields a **{savings_s1/additional_rrsp*100:.1f}%** immediate return (tax savings).")

    elif page == "Export Model":
        st.title("Excel Model")
        if st.button("Generate Excel File"):
            excel = generate_excel_model(d)
            st.download_button(label="Download Model", data=excel, file_name="Tax_Plan.xlsx")

elif auth_status is False:
    st.error("Username/password is incorrect")
elif auth_status is None:
    st.warning("Please enter your username and password")

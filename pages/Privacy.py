"""
Privacy Settings Page
"""

import streamlit as st

st.set_page_config(
    page_title="Privacy - AI Buddy",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Privacy Settings")

# Initialize session state if not present
if 'privacy' not in st.session_state:
    st.session_state.privacy = {
        "analytics": False,
        "save_progress": True,
        "email_reports": False
    }

# Data handling information
st.markdown("""
## Data Handling

We keep data only to personalize learning. You can view, export, or delete it from the Reports screen.

**What we collect:**
- Child's learning progress and activity outcomes
- Activity preferences and skill levels
- Session timestamps and duration

**What we don't collect:**
- Personal identifying information beyond names
- Location data
- Third-party tracking or advertising data

**Your control:**
- View all stored data in the Reports section
- Export your data at any time
- Delete specific records or all data
- Adjust privacy settings below
""")

st.markdown("---")

# Current privacy choices
st.subheader("Current Privacy Choices")

privacy = st.session_state.privacy

col1, col2 = st.columns(2)

with col1:
    st.write("**Analytics:**")
    st.write("Allow basic analytics (helps us improve)")
    st.write(f"Status: {'✅ Enabled' if privacy['analytics'] else '❌ Disabled'}")

with col2:
    st.write("**Save Progress:**")
    st.write("Save progress for personalized picks")
    st.write(f"Status: {'✅ Enabled' if privacy['save_progress'] else '❌ Disabled'}")

st.write("**Email Reports:**")
st.write("Email me weekly reports")
st.write(f"Status: {'✅ Enabled' if privacy['email_reports'] else '❌ Disabled'}")

st.markdown("---")

# Edit privacy settings
st.subheader("Edit Privacy Settings")

analytics = st.checkbox(
    "Allow basic analytics (helps us improve)",
    value=privacy["analytics"]
)
save_progress = st.checkbox(
    "Save progress for personalized picks",
    value=privacy["save_progress"]
)
email_reports = st.checkbox(
    "Email me weekly reports",
    value=privacy["email_reports"]
)

# Update session state when checkboxes change
if (analytics != privacy["analytics"] or 
    save_progress != privacy["save_progress"] or 
    email_reports != privacy["email_reports"]):
    st.session_state.privacy["analytics"] = analytics
    st.session_state.privacy["save_progress"] = save_progress
    st.session_state.privacy["email_reports"] = email_reports
    st.success("Privacy settings updated!")

st.markdown("---")

# Back to app button
if st.button("← Back to App", type="primary"):
    st.switch_page("streamlit_app.py")

"""
AI Buddy Streamlit App

A comprehensive web interface for the AI Buddy educational system.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import List, Optional, Tuple

# Import AI Buddy modules
from src.ai_buddy.loader import load_activities, load_profiles
from src.ai_buddy.persist import load_history, save_history, save_child_snapshot
from src.ai_buddy.recommender import recommend_activities, explain_recommendation
from src.ai_buddy.buddy import run_session_once, get_activity_intro, get_encouragement_and_tip
from src.ai_buddy.evaluate import eval_qna, eval_freeform, choose_outcome_from_eval
from src.ai_buddy.simulate import answer
from src.ai_buddy.report import generate_parent_report
from src.ai_buddy.data_models import Activity, ChildProfile
from src.ai_buddy.session import ActivityAttempt


# Page config
st.set_page_config(
    page_title="AI Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'selected_child' not in st.session_state:
    st.session_state.selected_child = None
if 'current_picks' not in st.session_state:
    st.session_state.current_picks = []
if 'last_report_paths' not in st.session_state:
    st.session_state.last_report_paths = []


def load_data() -> Tuple[List[Activity], List[ChildProfile], List]:
    """Load all data with error handling."""
    try:
        activities = load_activities("data/activities.json")
        profiles = load_profiles("data/profiles.json")
        history = load_history("data/history.json")
        return activities, profiles, history
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return [], [], []


def seed_demo_data():
    """Seed demo history data if empty."""
    try:
        history = load_history("data/history.json")
        if not history:
            # Create some demo session data
            from datetime import datetime, timedelta
            
            demo_attempts = [
                ActivityAttempt(
                    activity_id="reading_001",
                    timestamp=datetime.now() - timedelta(days=2),
                    outcome="success"
                ),
                ActivityAttempt(
                    activity_id="spelling_001", 
                    timestamp=datetime.now() - timedelta(days=1),
                    outcome="partial"
                ),
                ActivityAttempt(
                    activity_id="math_001",
                    timestamp=datetime.now() - timedelta(hours=6),
                    outcome="struggle"
                )
            ]
            
            from src.ai_buddy.session import SessionLog
            demo_session = SessionLog(
                child_id="child_001",
                attempts=demo_attempts
            )
            
            save_history([demo_session], "data/history.json")
            st.success("Demo data seeded successfully!")
            st.rerun()
        else:
            st.info("History already contains data.")
    except Exception as e:
        st.error(f"Failed to seed demo data: {str(e)}")


def run_activity_session(child: ChildProfile, activity: Activity, simulate: bool) -> Tuple[str, str, dict]:
    """Run a single activity session and return transcript and outcome."""
    try:
        # Get answer
        if simulate:
            user_answer = answer(child, activity)
        else:
            user_answer = st.text_input(f"Your answer for {activity.title}:", key=f"answer_{activity.id}")
            if not user_answer:
                return "", "", {}
        
        # Evaluate
        if activity.format == "qna":
            eval_result = eval_qna(user_answer, activity)
        else:
            eval_result = eval_freeform(user_answer, activity)
        
        outcome = choose_outcome_from_eval(eval_result)
        
        # Create transcript
        intro = get_activity_intro(activity)
        encouragement, tip = get_encouragement_and_tip(outcome)
        
        transcript = f"""
**Buddy:** {intro}

**You:** {user_answer}

**Outcome:** {outcome.title()} (Score: {eval_result.get('score', 'N/A')})

**Feedback:** {encouragement}
**Tip:** {tip}
"""
        
        return transcript, outcome, eval_result
        
    except Exception as e:
        st.error(f"Error running activity: {str(e)}")
        return "", "", {}


def get_skill_deltas(child_before: ChildProfile, child_after: ChildProfile) -> pd.DataFrame:
    """Get skill changes between before and after states."""
    deltas = []
    for skill in child_after.baseline_skills:
        before_val = child_before.baseline_skills.get(skill, 0.0)
        after_val = child_after.baseline_skills.get(skill, 0.0)
        delta = after_val - before_val
        deltas.append({
            'Skill': skill.replace('_', ' ').title(),
            'Before': f"{before_val:.3f}",
            'After': f"{after_val:.3f}",
            'Change': f"{delta:+.3f}"
        })
    
    return pd.DataFrame(deltas)


# Sidebar
with st.sidebar:
    st.title("🎓 AI Buddy")
    st.markdown("Educational AI Assistant")
    
    # Load data
    activities, profiles, history = load_data()
    
    if not activities or not profiles:
        st.error("Failed to load data. Please check your data files.")
        st.stop()
    
    # Child selection
    st.subheader("👤 Select Child")
    child_options = {f"{p.name} ({p.id})": p for p in profiles}
    selected_child_name = st.selectbox(
        "Choose a child:",
        options=list(child_options.keys()),
        index=0
    )
    st.session_state.selected_child = child_options[selected_child_name]
    
    # Simulation toggle
    simulate_answers = st.checkbox("Simulate answers", value=True)
    
    # Seed demo data button
    st.subheader("📊 Data Management")
    if st.button("Seed Demo Data"):
        seed_demo_data()
    
    # Display selected child info
    if st.session_state.selected_child:
        child = st.session_state.selected_child
        st.markdown("---")
        st.subheader("Child Info")
        st.write(f"**Name:** {child.name}")
        st.write(f"**Age:** {child.age}")
        st.write(f"**Learning Style:** {child.learning_style}")
        st.write(f"**Reading Level:** {child.reading_level}")
        st.write(f"**Attention Span:** {child.attention_span_min} min")


# Main content
if st.session_state.selected_child:
    child = st.session_state.selected_child
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 Recommendations", "🤖 Buddy Session", "📊 Parent Report"])
    
    # Tab 1: Recommendations
    with tab1:
        st.header("Activity Recommendations")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Refresh Picks"):
                st.session_state.current_picks = []
        
        # Get recommendations
        if not st.session_state.current_picks:
            try:
                st.session_state.current_picks = recommend_activities(child, activities, history, k=3)
            except Exception as e:
                st.error(f"Failed to get recommendations: {str(e)}")
                st.session_state.current_picks = []
        
        # Display recommendations
        if st.session_state.current_picks:
            for i, activity in enumerate(st.session_state.current_picks):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        ### {i+1}. {activity.title}
                        **Type:** {activity.type.title()} | **Level:** {activity.level.title()} | **Time:** {activity.estimated_min} min
                        """)
                        
                        # Explanation expander
                        with st.expander("Why this activity?"):
                            try:
                                explanation = explain_recommendation(child, activity, history)
                                st.write(explanation)
                            except Exception as e:
                                st.error(f"Failed to get explanation: {str(e)}")
                    
                    with col2:
                        st.write(f"**Skills:** {', '.join(activity.skills)}")
        else:
            st.warning("No recommendations available.")
    
    # Tab 2: Buddy Session
    with tab2:
        st.header("Interactive Learning Session")
        
        # Session controls
        col1, col2 = st.columns([2, 1])
        with col1:
            num_activities = st.radio("Number of activities:", [2, 3], horizontal=True)
        
        with col2:
            run_session = st.button("🚀 Run Session", type="primary")
        
        if run_session:
            if not st.session_state.current_picks:
                st.error("No activities selected. Please go to Recommendations tab first.")
            else:
                # Get selected activities
                selected_activities = st.session_state.current_picks[:num_activities]
                
                # Store original child state
                child_before = ChildProfile.model_validate(child.model_dump())
                
                # Session transcript
                st.subheader("Session Transcript")
                transcript_container = st.container()
                
                with transcript_container:
                    for i, activity in enumerate(selected_activities):
                        st.markdown(f"---")
                        st.markdown(f"### Activity {i+1}: {activity.title}")
                        
                        # Run activity
                        transcript, outcome, eval_result = run_activity_session(
                            child, activity, simulate_answers
                        )
                        
                        if transcript:
                            st.markdown(transcript)
                            
                            # Create and append attempt
                            attempt = ActivityAttempt(
                                activity_id=activity.id,
                                timestamp=datetime.now(),
                                outcome=outcome,
                                details={"eval": eval_result, "activity": activity.id}
                            )
                            
                            # Update history
                            history = load_history("data/history.json")
                            from src.ai_buddy.session import append_attempt
                            history = append_attempt(history, child.id, attempt)
                            save_history(history, "data/history.json")
                            
                            # Update child skills
                            delta_map = {
                                "success": 0.03,
                                "partial": 0.01,
                                "struggle": -0.01,
                                "skipped": 0.0
                            }
                            delta = delta_map.get(outcome, 0.0)
                            
                            for skill in activity.skills:
                                current_skill = child.baseline_skills.get(skill, 0.5)
                                new_skill = max(0.0, min(1.0, current_skill + delta))
                                child.baseline_skills[skill] = new_skill
                
                # Show skill changes
                st.subheader("Skill Changes")
                skill_df = get_skill_deltas(child_before, child)
                st.dataframe(skill_df, use_container_width=True)
                
                # Save final state
                try:
                    save_child_snapshot(child, f"data/snapshots/{child.id}.json")
                    st.success("✅ Session completed! Progress saved.")
                except Exception as e:
                    st.error(f"Failed to save progress: {str(e)}")
    
    # Tab 3: Parent Report
    with tab3:
        st.header("Parent Report Generator")
        
        # Report controls
        col1, col2, col3 = st.columns(3)
        with col1:
            period = st.selectbox("Time Period:", ["7d", "14d", "30d"])
        with col2:
            report_format = st.selectbox("Format:", ["md", "json", "both"])
        with col3:
            generate_report = st.button("📄 Generate Report", type="primary")
        
        if generate_report:
            try:
                # Generate report
                report_paths = generate_parent_report(
                    child, activities, history, 
                    period=period, out_dir="reports", fmt=report_format
                )
                
                st.session_state.last_report_paths = report_paths
                
                st.success(f"✅ Report generated! {len(report_paths)} file(s) created.")
                
                # Display markdown preview if available
                md_path = next((p for p in report_paths if p.suffix == '.md'), None)
                if md_path and md_path.exists():
                    st.subheader("Report Preview")
                    with open(md_path, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    st.markdown(report_content)
                
                # Download buttons
                st.subheader("Download Reports")
                for path in report_paths:
                    if path.exists():
                        with open(path, 'rb') as f:
                            file_bytes = f.read()
                        
                        file_label = f"Download {path.suffix.upper().replace('.', '')}"
                        st.download_button(
                            label=file_label,
                            data=file_bytes,
                            file_name=path.name,
                            mime="text/plain" if path.suffix == '.md' else "application/json"
                        )
                
            except Exception as e:
                st.error(f"Failed to generate report: {str(e)}")

else:
    st.info("Please select a child from the sidebar to begin.")

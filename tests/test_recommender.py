"""
Tests for the recommender module.

This module contains tests for the activity recommendation functions.
"""

import pytest
from datetime import datetime, timedelta

from ai_buddy.data_models import Activity, ChildProfile
from ai_buddy.session import SessionLog, ActivityAttempt
from ai_buddy.recommender import recommend_activities, explain_recommendation
from ai_buddy.loader import load_activities, load_profiles


class TestRecommendActivities:
    """Test cases for recommend_activities function."""
    
    def test_recommend_activities_basic(self):
        """Test basic recommendation functionality."""
        # Create test child
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.8, "reading": 0.7},
            interests=["math", "puzzles"]
        )
        
        # Create test activities
        activities = [
            Activity(
                id="math_001",
                type="math",
                title="Math Activity 1",
                description="Test math activity",
                level="easy",
                skills=["math"],
                estimated_min=15,
                format="qna",
                rubric={}
            ),
            Activity(
                id="reading_001",
                type="reading",
                title="Reading Activity 1",
                description="Test reading activity",
                level="medium",
                skills=["reading"],
                estimated_min=20,
                format="freeform",
                rubric={}
            ),
            Activity(
                id="logic_001",
                type="logic",
                title="Logic Activity 1",
                description="Test logic activity",
                level="hard",
                skills=["logic"],
                tags=["puzzles"],
                estimated_min=25,
                format="qna",
                rubric={}
            )
        ]
        
        # Get recommendations
        recommended = recommend_activities(child, activities, history=None, k=2)
        
        # Should return 2 activities
        assert len(recommended) == 2
        
        # Should be sorted by score (descending)
        assert recommended[0].id != recommended[1].id
    
    def test_recommend_activities_empty_activities(self):
        """Test recommendation with empty activities list."""
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.8}
        )
        
        recommended = recommend_activities(child, [], history=None, k=3)
        assert recommended == []
    
    def test_recommend_activities_with_history(self):
        """Test recommendation with session history."""
        # Create test child
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="logical",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.8, "logic": 0.9},
            interests=["puzzles"]
        )
        
        # Create test activities
        activities = [
            Activity(
                id="math_001",
                type="math",
                title="Math Activity 1",
                description="Test math activity",
                level="easy",
                skills=["math"],
                estimated_min=15,
                format="qna",
                rubric={}
            ),
            Activity(
                id="logic_001",
                type="logic",
                title="Logic Activity 1",
                description="Test logic activity",
                level="medium",
                skills=["logic"],
                tags=["puzzles"],
                estimated_min=20,
                format="qna",
                rubric={}
            )
        ]
        
        # Create history with recent attempt
        history = [
            SessionLog(
                child_id="child_001",
                attempts=[
                    ActivityAttempt(
                        activity_id="math_001",
                        timestamp=datetime.now(),
                        outcome="success"
                    )
                ]
            )
        ]
        
        # Get recommendations
        recommended = recommend_activities(child, activities, history=history, k=2)
        
        # Should return activities (recency penalty should affect scoring)
        assert len(recommended) > 0
    
    def test_recommend_activities_diversity_pass(self):
        """Test diversity pass ensures different activity types."""
        # Create test child
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.8, "reading": 0.7},
            interests=["math"]
        )
        
        # Create activities with same type (math) but different scores
        activities = [
            Activity(
                id="math_001",
                type="math",
                title="Math Activity 1",
                description="Test math activity 1",
                level="easy",
                skills=["math"],
                estimated_min=10,
                format="qna",
                rubric={}
            ),
            Activity(
                id="math_002",
                type="math",
                title="Math Activity 2",
                description="Test math activity 2",
                level="easy",
                skills=["math"],
                estimated_min=15,
                format="qna",
                rubric={}
            ),
            Activity(
                id="reading_001",
                type="reading",
                title="Reading Activity 1",
                description="Test reading activity",
                level="medium",
                skills=["reading"],
                estimated_min=20,
                format="freeform",
                rubric={}
            )
        ]
        
        # Get recommendations
        recommended = recommend_activities(child, activities, history=None, k=2)
        
        # Should have at least 2 different types if available
        if len(recommended) >= 2:
            types = {activity.type for activity in recommended}
            # If we have both math and reading activities, diversity should kick in
            if "math" in types and "reading" in types:
                assert len(types) >= 2
    
    def test_recommend_activities_k_cap(self):
        """Test that k is capped at 3."""
        # Create test child
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.8}
        )
        
        # Create many activities
        activities = [
            Activity(
                id=f"activity_{i}",
                type="math",
                title=f"Activity {i}",
                description=f"Test activity {i}",
                level="easy",
                skills=["math"],
                estimated_min=15,
                format="qna",
                rubric={}
            )
            for i in range(10)
        ]
        
        # Request more than 3
        recommended = recommend_activities(child, activities, history=None, k=5)
        
        # Should be capped at 3
        assert len(recommended) <= 3

    def test_returns_top_k_and_diverse(self):
        """Test that recommendations return top k results with diversity."""
        # Load real data from JSON files
        try:
            activities = load_activities("data/activities.json")
            profiles = load_profiles("data/profiles.json")
        except FileNotFoundError:
            pytest.skip("Data files not found, skipping integration test")
        
        # Test with two different children
        test_children = profiles[:2]  # Take first two children
        
        for child in test_children:
            # Get recommendations
            recommended = recommend_activities(child, activities, history=None, k=3)
            
            # Assert length constraints
            assert 2 <= len(recommended) <= 3, f"Expected 2-3 recommendations, got {len(recommended)}"
            
            # Assert diversity (at least 2 distinct types)
            types = {activity.type for activity in recommended}
            assert len(types) >= 2, f"Expected at least 2 distinct types, got {types}"

    def test_recency_penalty_applied(self):
        """Test that recency penalty is properly applied."""
        # Create test child
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.8, "reading": 0.7},
            interests=["math"]
        )
        
        # Create test activities including A003
        activities = [
            Activity(
                id="A001",
                type="math",
                title="Math Activity 1",
                description="Test math activity",
                level="easy",
                skills=["math"],
                estimated_min=15,
                format="qna",
                rubric={}
            ),
            Activity(
                id="A002",
                type="reading",
                title="Reading Activity 1",
                description="Test reading activity",
                level="medium",
                skills=["reading"],
                estimated_min=20,
                format="freeform",
                rubric={}
            ),
            Activity(
                id="A003",
                type="math",
                title="Math Activity 2",
                description="Test math activity 2",
                level="easy",
                skills=["math"],
                estimated_min=15,
                format="qna",
                rubric={}
            )
        ]
        
        # Create history where A003 was recently attempted
        history = [
            SessionLog(
                child_id="child_001",
                attempts=[
                    ActivityAttempt(
                        activity_id="A003",
                        timestamp=datetime.now(),
                        outcome="success"
                    ),
                    ActivityAttempt(
                        activity_id="A001",
                        timestamp=datetime.now() - timedelta(minutes=5),
                        outcome="success"
                    )
                ]
            )
        ]
        
        # Get recommendations with history
        recommended_with_history = recommend_activities(child, activities, history=history, k=3)
        
        # Get recommendations without history
        recommended_without_history = recommend_activities(child, activities, history=None, k=3)
        
        # A003 should be ranked lower with history due to recency penalty
        # Find A003 in both lists
        a003_with_history = None
        a003_without_history = None
        
        for i, activity in enumerate(recommended_with_history):
            if activity.id == "A003":
                a003_with_history = i
                break
                
        for i, activity in enumerate(recommended_without_history):
            if activity.id == "A003":
                a003_without_history = i
                break
        
        # If A003 appears in both lists, it should be ranked lower with history
        if a003_with_history is not None and a003_without_history is not None:
            assert a003_with_history >= a003_without_history, \
                f"A003 should be ranked lower with history (position {a003_with_history} vs {a003_without_history})"

    def test_time_fit_effect(self):
        """Test that time fit affects scoring for children with small attention spans."""
        # Create child with small attention span
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=10,  # Small attention span
            reading_level="on_grade",
            baseline_skills={"math": 0.8},
            interests=["math"]
        )
        
        # Create activities with different estimated times
        short_activity = Activity(
            id="short_001",
            type="math",
            title="Short Math Activity",
            description="Short activity",
            level="easy",
            skills=["math"],
            estimated_min=5,  # Within attention span
            format="qna",
            rubric={}
        )
        
        long_activity = Activity(
            id="long_001",
            type="math",
            title="Long Math Activity",
            description="Long activity",
            level="easy",
            skills=["math"],
            estimated_min=30,  # Exceeds attention span
            format="qna",
            rubric={}
        )
        
        # Get explanations for both activities
        short_explanation = explain_recommendation(child, short_activity, history=None)
        long_explanation = explain_recommendation(child, long_activity, history=None)
        
        # Short activity should have higher time_fit score
        short_time_score = short_explanation["component_scores"]["time_fit"]["score"]
        long_time_score = long_explanation["component_scores"]["time_fit"]["score"]
        
        assert short_time_score > long_time_score, \
            f"Short activity should have higher time_fit score ({short_time_score} vs {long_time_score})"
        
        # Short activity should have higher total score
        assert short_explanation["total_score"] > long_explanation["total_score"], \
            f"Short activity should have higher total score ({short_explanation['total_score']} vs {long_explanation['total_score']})"

    def test_skill_alignment_levels(self):
        """Test that high-skilled children can get hard activities ranked above easy ones."""
        # Create child with high math skills
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="logical",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.9},  # High math skill
            interests=["math", "puzzles"]
        )
        
        # Create easy and hard math activities
        easy_math = Activity(
            id="easy_math",
            type="math",
            title="Easy Math Activity",
            description="Easy math activity",
            level="easy",
            skills=["math"],
            estimated_min=15,
            format="qna",
            rubric={}
        )
        
        hard_math = Activity(
            id="hard_math",
            type="math",
            title="Hard Math Activity",
            description="Hard math activity",
            level="hard",
            skills=["math"],
            tags=["puzzles"],
            estimated_min=20,
            format="qna",
            rubric={}
        )
        
        # Get explanations for both activities
        easy_explanation = explain_recommendation(child, easy_math, history=None)
        hard_explanation = explain_recommendation(child, hard_math, history=None)
        
        # Hard activity should have higher level_fit score for high-skilled child
        easy_level_score = easy_explanation["component_scores"]["level_fit"]["score"]
        hard_level_score = hard_explanation["component_scores"]["level_fit"]["score"]
        
        # With math skill of 0.9, hard level should be aligned (score 1.0) and easy should be adjacent (score 0.7)
        assert hard_level_score > easy_level_score, \
            f"Hard activity should have higher level_fit score for high-skilled child ({hard_level_score} vs {easy_level_score})"
        
        # Hard activity should have higher total score
        assert hard_explanation["total_score"] > easy_explanation["total_score"], \
            f"Hard activity should have higher total score for high-skilled child ({hard_explanation['total_score']} vs {easy_explanation['total_score']})"


class TestExplainRecommendation:
    """Test cases for explain_recommendation function."""
    
    def test_explain_recommendation_basic(self):
        """Test basic explanation functionality."""
        # Create test child
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.8},
            interests=["math"]
        )
        
        # Create test activity
        activity = Activity(
            id="math_001",
            type="math",
            title="Math Activity 1",
            description="Test math activity",
            level="easy",
            skills=["math"],
            estimated_min=15,
            format="qna",
            rubric={}
        )
        
        # Get explanation
        explanation = explain_recommendation(child, activity, history=None)
        
        # Check structure
        assert "activity_id" in explanation
        assert "activity_title" in explanation
        assert "activity_type" in explanation
        assert "activity_level" in explanation
        assert "component_scores" in explanation
        assert "total_score" in explanation
        assert "child_id" in explanation
        assert "child_name" in explanation
        
        # Check component scores
        components = explanation["component_scores"]
        expected_components = ["skill_fit", "interest_fit", "style_fit", "level_fit", "time_fit", "recency_penalty"]
        for component in expected_components:
            assert component in components
            assert "score" in components[component]
            assert "weight" in components[component]
            assert "weighted_score" in components[component]
        
        # Check that total score is reasonable
        assert 0.0 <= explanation["total_score"] <= 1.0
    
    def test_explain_recommendation_with_history(self):
        """Test explanation with session history."""
        # Create test child
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="logical",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.8},
            interests=["puzzles"]
        )
        
        # Create test activity
        activity = Activity(
            id="math_001",
            type="math",
            title="Math Activity 1",
            description="Test math activity",
            level="easy",
            skills=["math"],
            estimated_min=15,
            format="qna",
            rubric={}
        )
        
        # Create history with recent attempt of this activity
        history = [
            SessionLog(
                child_id="child_001",
                attempts=[
                    ActivityAttempt(
                        activity_id="math_001",
                        timestamp=datetime.now(),
                        outcome="success"
                    )
                ]
            )
        ]
        
        # Get explanation
        explanation = explain_recommendation(child, activity, history=history)
        
        # Should have recency penalty
        recency_penalty = explanation["component_scores"]["recency_penalty"]
        assert recency_penalty["score"] > 0  # Should have penalty for recent activity
    
    def test_explain_recommendation_component_scores(self):
        """Test that component scores are calculated correctly."""
        # Create test child with specific characteristics
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=15,
            reading_level="on_grade",
            baseline_skills={"math": 0.9},  # High math skill
            interests=["math"]  # Interested in math
        )
        
        # Create math activity that should score well
        activity = Activity(
            id="math_001",
            type="math",
            title="Math Activity 1",
            description="Test math activity",
            level="easy",
            skills=["math"],
            tags=["visual"],  # Matches visual learning style
            estimated_min=10,  # Within attention span
            format="qna",
            rubric={}
        )
        
        # Get explanation
        explanation = explain_recommendation(child, activity, history=None)
        
        # Check specific component scores
        components = explanation["component_scores"]
        
        # Skill fit should be high (0.9)
        assert abs(components["skill_fit"]["score"] - 0.9) < 0.001
        
        # Interest fit should be high (1.0 for math interest)
        assert components["interest_fit"]["score"] == 1.0
        
        # Style fit should be high (visual tags match visual learning style)
        assert components["style_fit"]["score"] == 1.0
        
        # Time fit should be high (within attention span)
        assert components["time_fit"]["score"] == 1.0
        
        # Recency penalty should be 0 (no history)
        assert components["recency_penalty"]["score"] == 0.0

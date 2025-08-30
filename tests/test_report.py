import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
from unittest.mock import patch

from ai_buddy.data_models import Activity, ChildProfile
from ai_buddy.session import SessionLog, ActivityAttempt
from ai_buddy.report import generate_parent_report


@pytest.fixture
def sample_activities():
    """Sample activities for testing"""
    return [
        Activity(
            id="A001",
            title="Word Building",
            type="spelling",
            level="easy",
            description="Build words using letter tiles",
            skills=["spelling", "pattern_recognition"],
            tags=["words", "letters"],
            estimated_min=5,
            format="qna",
            rubric={"spelling": 0.7, "pattern_recognition": 0.3}
        ),
        Activity(
            id="A002", 
            title="Number Stories",
            type="math",
            level="easy",
            description="Solve math problems through storytelling",
            skills=["addition", "storytelling"],
            tags=["numbers", "stories"],
            estimated_min=8,
            format="qna",
            rubric={"addition": 0.6, "storytelling": 0.4}
        ),
        Activity(
            id="A003",
            title="Logic Puzzles",
            type="logic",
            level="medium", 
            description="Solve logical reasoning puzzles",
            skills=["logic", "pattern_recognition"],
            tags=["puzzles", "thinking"],
            estimated_min=10,
            format="qna",
            rubric={"logic": 0.8, "pattern_recognition": 0.2}
        )
    ]


@pytest.fixture
def sample_profiles():
    """Sample child profiles for testing"""
    return [
        ChildProfile(
            id="C001",
            name="Alex",
            age=7,
            grade=2,
            interests=["puzzles", "stories"],
            learning_style="visual",
            attention_span_min=10,
            reading_level="on_grade",
            baseline_skills={"spelling": 0.6, "logic": 0.4, "addition": 0.7}
        )
    ]


@pytest.fixture
def sample_history():
    """Sample session history with attempts within last 7 days"""
    now = datetime.now(timezone.utc)
    return [
        SessionLog(
            child_id="C001",
            attempts=[
                ActivityAttempt(
                    activity_id="A001",
                    timestamp=now - timedelta(days=2, minutes=5),
                    outcome="success"
                ),
                ActivityAttempt(
                    activity_id="A002", 
                    timestamp=now - timedelta(days=1, minutes=10),
                    outcome="success"
                ),
                ActivityAttempt(
                    activity_id="A003",
                    timestamp=now - timedelta(hours=6),
                    outcome="struggle"
                )
            ]
        )
    ]


def test_generates_md_and_json(tmp_path, sample_activities, sample_profiles, sample_history):
    """Test that generate_parent_report creates both markdown and JSON files with expected content"""
    child = sample_profiles[0]
    
    # Mock the recommender to return predictable results
    with patch('ai_buddy.report.recommend_activities') as mock_recommend:
        mock_recommend.return_value = sample_activities[:2]  # Return first 2 activities
        
        paths = generate_parent_report(
            child, 
            sample_activities, 
            sample_history, 
            period="7d", 
            out_dir=str(tmp_path), 
            fmt="both"
        )
    
    # Assert two files were created
    assert len(paths) == 2
    
    # Check markdown file
    md_path = next(p for p in paths if p.suffix == '.md')
    assert md_path.exists()
    md_content = md_path.read_text(encoding='utf-8')
    assert len(md_content) > 0
    assert "Parent Report — Alex" in md_content
    assert "Highlights" in md_content
    assert "Recommended Next Activities" in md_content
    
    # Check JSON file
    json_path = next(p for p in paths if p.suffix == '.json')
    assert json_path.exists()
    json_content = json.loads(json_path.read_text(encoding='utf-8'))
    
    # Assert required keys exist
    required_keys = ["child_id", "skills", "types", "recommended"]
    for key in required_keys:
        assert key in json_content
    
    # Assert specific values
    assert json_content["child_id"] == "C001"
    assert isinstance(json_content["skills"], dict)
    assert isinstance(json_content["types"], dict)
    assert isinstance(json_content["recommended"], list)


def test_sparks_and_focus_classification(tmp_path, sample_activities, sample_profiles):
    """Test that skills are correctly classified as sparks (high performance) and focus areas (low performance)"""
    child = sample_profiles[0]
    
    # Create history with clear skill performance differences
    now = datetime.now(timezone.utc)
    history = [
        SessionLog(
            child_id="C001",
            attempts=[
                # High performing skill: spelling (2 attempts, both success = 1.0 avg)
                ActivityAttempt(
                    activity_id="A001",  # spelling activity
                    timestamp=now - timedelta(days=1, minutes=10),
                    outcome="success"
                ),
                ActivityAttempt(
                    activity_id="A001",  # spelling activity again
                    timestamp=now - timedelta(days=1, minutes=5), 
                    outcome="success"
                ),
                # Low performing skill: logic (2 attempts, both struggle = 0.2 avg)
                ActivityAttempt(
                    activity_id="A003",  # logic activity
                    timestamp=now - timedelta(hours=12),
                    outcome="struggle"
                ),
                ActivityAttempt(
                    activity_id="A003",  # logic activity again
                    timestamp=now - timedelta(hours=6),
                    outcome="struggle"
                )
            ]
        )
    ]
    
    # Mock recommender
    with patch('ai_buddy.report.recommend_activities') as mock_recommend:
        mock_recommend.return_value = sample_activities[:1]
        
        paths = generate_parent_report(
            child,
            sample_activities,
            history,
            period="7d",
            out_dir=str(tmp_path),
            fmt="md"
        )
    
    # Read markdown content
    md_path = paths[0]
    md_content = md_path.read_text(encoding='utf-8')
    
    # Assert sparks contains the high-performing skill
    assert "Sparks:" in md_content
    # spelling should be in sparks (high avg >= 0.75)
    assert "spelling" in md_content.lower() or "Spelling" in md_content
    
    # Assert growth areas contains the low-performing skill  
    assert "Growth areas:" in md_content
    # logic should be in focus areas (low avg <= 0.5)
    assert "logic" in md_content.lower() or "Logic" in md_content


def test_recommender_integration(tmp_path, sample_activities, sample_profiles, sample_history):
    """Test that recommended activities are valid and within expected range"""
    child = sample_profiles[0]
    
    # Mock recommender to return specific activities
    with patch('ai_buddy.report.recommend_activities') as mock_recommend:
        mock_recommend.return_value = sample_activities[:2]  # Return 2 activities
        
        paths = generate_parent_report(
            child,
            sample_activities,
            sample_history,
            period="7d",
            out_dir=str(tmp_path),
            fmt="json"
        )
    
    # Read JSON content
    json_path = paths[0]
    json_content = json.loads(json_path.read_text(encoding='utf-8'))
    
    # Assert recommended activities exist and are valid
    recommended = json_content["recommended"]
    assert isinstance(recommended, list)
    assert 1 <= len(recommended) <= 3
    
    # Assert all recommended IDs are from the activities set
    activity_ids = {a.id for a in sample_activities}
    for rec_id in recommended:
        assert rec_id in activity_ids
    
    # Verify recommender was called correctly
    mock_recommend.assert_called_once()
    call_args = mock_recommend.call_args
    assert call_args[0][0] == child  # first arg should be child
    assert call_args[0][1] == sample_activities  # second arg should be activities
    assert call_args[0][2] == sample_history  # third arg should be history
    assert call_args[1]['k'] == 3  # k parameter should be 3

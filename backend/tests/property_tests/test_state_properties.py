"""
Property-based tests for Global State management.

Tests verify universal properties of the GlobalState model including
serialization, validation, and data integrity.
"""

import json
from datetime import datetime, timezone
from hypothesis import given, strategies as st
from hypothesis.strategies import SearchStrategy
import pytest

from backend.models.state import GlobalState


# Custom strategies for GlobalState fields
def datetime_strategy() -> SearchStrategy:
    """Generate valid datetime objects (naive datetimes)."""
    return st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    )


def risk_level_strategy() -> SearchStrategy:
    """Generate valid risk level values."""
    return st.one_of(
        st.none(),
        st.sampled_from(["low", "medium", "high"])
    )


def regulatory_model_strategy() -> SearchStrategy:
    """Generate valid regulatory model dictionaries."""
    return st.one_of(
        st.none(),
        st.fixed_dictionaries({
            "title": st.text(min_size=1, max_size=100),
            "description": st.text(min_size=1, max_size=500),
            "requirements": st.lists(st.text(min_size=1, max_size=200), min_size=0, max_size=10),
            "deadlines": st.lists(
                st.fixed_dictionaries({
                    "date": st.dates().map(lambda d: d.isoformat()),
                    "description": st.text(min_size=1, max_size=100)
                }),
                min_size=0,
                max_size=5
            ),
            "affected_systems": st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10)
        })
    )


def impacted_file_strategy() -> SearchStrategy:
    """Generate valid impacted file dictionaries."""
    return st.fixed_dictionaries({
        "file_path": st.text(min_size=1, max_size=200),
        "relevance_score": st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        "snippet": st.text(min_size=0, max_size=200)
    })


def impact_strategy() -> SearchStrategy:
    """Generate valid impact analysis dictionaries."""
    return st.fixed_dictionaries({
        "file_path": st.text(min_size=1, max_size=200),
        "impact_type": st.sampled_from(["schema_change", "business_logic", "validation", "api_contract"]),
        "severity": st.sampled_from(["low", "medium", "high"]),
        "description": st.text(min_size=1, max_size=500),
        "suggested_changes": st.lists(st.text(min_size=1, max_size=200), min_size=0, max_size=10)
    })


def global_state_strategy() -> SearchStrategy:
    """Generate valid GlobalState instances."""
    return st.builds(
        GlobalState,
        raw_regulatory_text=st.text(min_size=1, max_size=10000),
        change_detected=st.one_of(st.none(), st.booleans()),
        risk_level=risk_level_strategy(),
        regulatory_model=regulatory_model_strategy(),
        impacted_files=st.lists(impacted_file_strategy(), min_size=0, max_size=10),
        impact_analysis=st.lists(impact_strategy(), min_size=0, max_size=20),
        technical_spec=st.one_of(st.none(), st.text(min_size=0, max_size=5000)),
        kiro_prompt=st.one_of(st.none(), st.text(min_size=0, max_size=5000)),
        execution_timestamp=datetime_strategy(),
        execution_id=st.one_of(st.none(), st.uuids().map(str)),
        error=st.one_of(st.none(), st.text(min_size=0, max_size=500))
    )


# **Validates: Requirements 15.4**
# Property 34: Global State Serialization Round-Trip
@given(global_state_strategy())
def test_global_state_serialization_round_trip(state: GlobalState):
    """
    For any GlobalState object, serializing to JSON then deserializing
    should produce an equivalent state with all fields preserved and correct types.
    
    This property ensures that GlobalState can be reliably stored in the Audit_Log
    and retrieved without data loss or corruption.
    """
    # Serialize to JSON string
    json_str = state.model_dump_json()
    
    # Verify it's valid JSON
    json_data = json.loads(json_str)
    assert isinstance(json_data, dict)
    
    # Deserialize back to GlobalState
    restored_state = GlobalState.model_validate_json(json_str)
    
    # Verify all fields are preserved
    assert restored_state.raw_regulatory_text == state.raw_regulatory_text
    assert restored_state.change_detected == state.change_detected
    assert restored_state.risk_level == state.risk_level
    assert restored_state.regulatory_model == state.regulatory_model
    assert restored_state.impacted_files == state.impacted_files
    assert restored_state.impact_analysis == state.impact_analysis
    assert restored_state.technical_spec == state.technical_spec
    assert restored_state.kiro_prompt == state.kiro_prompt
    assert restored_state.execution_id == state.execution_id
    assert restored_state.error == state.error
    
    # Verify datetime is preserved (allowing for microsecond precision differences)
    # Pydantic may normalize datetime during serialization
    assert abs((restored_state.execution_timestamp - state.execution_timestamp).total_seconds()) < 0.001
    
    # Verify the restored state equals the original
    # Note: We compare field by field instead of direct equality due to datetime handling
    assert restored_state.model_dump() == state.model_dump()


@given(global_state_strategy())
def test_global_state_json_is_valid(state: GlobalState):
    """
    For any GlobalState object, the JSON serialization should be valid JSON
    that can be parsed without errors.
    """
    json_str = state.model_dump_json()
    
    # Should not raise an exception
    json_data = json.loads(json_str)
    
    # Should be a dictionary
    assert isinstance(json_data, dict)
    
    # Should contain all required fields
    assert "raw_regulatory_text" in json_data
    assert "execution_timestamp" in json_data


@given(global_state_strategy())
def test_global_state_preserves_types(state: GlobalState):
    """
    For any GlobalState object, after round-trip serialization,
    all field types should be preserved correctly.
    """
    json_str = state.model_dump_json()
    restored_state = GlobalState.model_validate_json(json_str)
    
    # Check types are preserved
    assert type(restored_state.raw_regulatory_text) == str
    assert restored_state.change_detected is None or type(restored_state.change_detected) == bool
    assert restored_state.risk_level is None or type(restored_state.risk_level) == str
    assert restored_state.regulatory_model is None or type(restored_state.regulatory_model) == dict
    assert type(restored_state.impacted_files) == list
    assert type(restored_state.impact_analysis) == list
    assert restored_state.technical_spec is None or type(restored_state.technical_spec) == str
    assert restored_state.kiro_prompt is None or type(restored_state.kiro_prompt) == str
    assert type(restored_state.execution_timestamp) == datetime
    assert restored_state.execution_id is None or type(restored_state.execution_id) == str
    assert restored_state.error is None or type(restored_state.error) == str


@given(
    st.text(min_size=1, max_size=1000),
    st.one_of(st.none(), st.booleans()),
    risk_level_strategy()
)
def test_global_state_minimal_serialization(
    raw_text: str,
    change_detected: bool | None,
    risk_level: str | None
):
    """
    For any minimal GlobalState (only required fields set),
    serialization should work correctly.
    """
    state = GlobalState(
        raw_regulatory_text=raw_text,
        change_detected=change_detected,
        risk_level=risk_level
    )
    
    json_str = state.model_dump_json()
    restored_state = GlobalState.model_validate_json(json_str)
    
    assert restored_state.raw_regulatory_text == raw_text
    assert restored_state.change_detected == change_detected
    assert restored_state.risk_level == risk_level


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

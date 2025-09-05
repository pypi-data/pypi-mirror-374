import os
import json
import pandas as pd
import pytest

from tsq.data_card import (
    generate_data_card,
    save_data_card_json,
    save_data_card_html,
    save_data_card_latex,
)


def make_df():
    """Fixture: Create a dataset with 2 entities (AAPL, MSFT) and 2 variables (close, volume)."""
    timestamps = pd.date_range("2025-01-01", periods=3, freq="D")
    df = pd.DataFrame({
        "timestamp": list(timestamps) * 4,  # repeat for all combos
        "entity": ["AAPL"] * 6 + ["MSFT"] * 6,
        "variable": ["close", "volume"] * 6,
        "value": [100, 200, 101, 202, None, 204, 50, 55, 53, 57, 59, None],
    })
    return df


# --- Unit Tests ---

def test_generate_data_card_overview():
    """Check that dataset-level overview (obs, entities, variables, time range) is computed correctly."""
    df = make_df()
    card = generate_data_card(df, "Test Multi")

    assert card["dataset_name"] == "Test Multi"
    assert card["overview"]["n_observations"] == len(df)
    assert card["overview"]["n_entities"] == 2
    assert card["overview"]["n_variables"] == 2
    assert card["overview"]["time_range"][0] is not None
    assert card["overview"]["time_range"][1] is not None


def test_generate_data_card_data_quality():
    """Validate data quality checks (missing values, duplicates, monotonicity)."""
    df = make_df()
    card = generate_data_card(df, "Test Multi")
    dq = card["data_quality"]

    assert dq["missing_values"] > 0
    assert dq["duplicates"] == 0
    assert isinstance(dq["timestamps_monotonic"], bool)


def test_generate_data_card_variable_stats():
    """Ensure variable-level stats (obs count, missing, min, max) are produced per variable."""
    df = make_df()
    card = generate_data_card(df, "Test Multi")

    assert "close" in card["variables"]
    assert "volume" in card["variables"]

    close_stats = card["variables"]["close"]
    volume_stats = card["variables"]["volume"]

    assert close_stats["n_observations"] > 0
    assert volume_stats["n_observations"] > 0
    assert close_stats["n_missing"] >= 0
    assert volume_stats["n_missing"] >= 0


def test_save_data_card_json(tmp_path):
    """Check that data card can be saved as JSON and reloaded correctly."""
    df = make_df()
    path = tmp_path / "card.json"
    save_data_card_json(df, "Test Multi", path)

    assert path.exists()
    with open(path) as f:
        card = json.load(f)
    assert card["dataset_name"] == "Test Multi"
    assert "close" in card["variables"]


def test_save_data_card_html(tmp_path):
    """Check that data card can be exported to HTML with key content present."""
    df = make_df()
    path = tmp_path / "card.html"
    save_data_card_html(df, "Test Multi", path)

    assert path.exists()
    content = path.read_text()
    assert "<html" in content.lower()
    assert "Test Multi" in content


def test_save_data_card_latex(tmp_path):
    """Check that data card can be exported to LaTeX with expected section and table."""
    df = make_df()
    path = tmp_path / "card.tex"
    save_data_card_latex(df, "Test Multi", path)

    assert path.exists()
    tex = path.read_text()
    assert "\\section*{Data Card: Test Multi}" in tex
    assert "Variable-level statistics" in tex


def test_invalid_input_columns():
    """Ensure function raises ValueError if required columns are missing."""
    df = pd.DataFrame({"time": [1, 2], "val": [3, 4]})
    with pytest.raises(ValueError):
        generate_data_card(df)

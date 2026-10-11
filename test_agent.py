
import pandas as pd
from agent import answer_question


def sample_data():
    return pd.DataFrame({
        "region": ["East", "West", "East", "North"],
        "sales": [100, 300, 200, 150],
        "profit": [10, 60, 30, 20],
    })


def test_total_sales():
    result = answer_question(
        sample_data(), "What is the total sales?"
    )
    assert "750.00" in result["answer"]


def test_average_profit():
    result = answer_question(
        sample_data(), "What is average profit?"
    )
    assert "30.00" in result["answer"]


def test_highest_sales_by_region():
    result = answer_question(
        sample_data(), "Which region has the highest sales?"
    )
    assert "West" in result["answer"]
    assert "300.00" in result["answer"]


def test_missing_values():
    result = answer_question(
        sample_data(), "How many missing values?"
    )
    assert "0 missing cells" in result["answer"]







import re
import pandas as pd


def answer_question(df, question):
    """Answer common analytical questions from a dataframe."""
    q = question.lower().strip()

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_cols = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    if not q:
        return {"answer": "Please enter a question."}

    if any(word in q for word in [
        "missing", "null", "duplicate", "data quality"
    ]):
        return {
            "answer": (
                f"Dataset contains {int(df.isna().sum().sum())} "
                f"missing cells and {int(df.duplicated().sum())} "
                "duplicate rows."
            )
        }

    # Group-by questions: highest/lowest sales by region, etc.
    group_match = re.search(
        r"\b(?:by|per|across)\s+([a-zA-Z_ ]+?)(?:\?|$)",
        q
    )

    metric = next(
        (col for col in numeric_cols if col in q),
        None
    )

    group_col = None
    if group_match:
        candidate = group_match.group(1).strip()
        group_col = next(
            (
                col for col in categorical_cols
                if col == candidate
                or col.replace("_", " ") == candidate
            ),
            None
        )
    else:
        group_col = next(
            (
                col for col in categorical_cols
                if re.search(
                    rf"\bwhich\s+{re.escape(col.replace('_', ' '))}\b",
                    q,
                )
            ),
            None,
        )

    if group_col and metric:
        grouped = (
            df.groupby(group_col, dropna=False)[metric]
            .sum()
        )

        if any(word in q for word in [
            "lowest", "least", "minimum", "worst"
        ]):
            value = grouped.min()
            direction = "Lowest"
        else:
            value = grouped.max()
            direction = "Highest"

        if pd.isna(value):
            return {"answer": "No valid groups found."}

        leaders = grouped[grouped == value].index
        categories = ", ".join(str(category) for category in leaders)

        return {
            "answer": (
                f"{direction} {metric} by {group_col}: "
                f"{categories} ({value:,.2f})."
            ),
            "table": grouped.rename(
                metric
            ).reset_index()
        }

    # Top-N questions
    if "top" in q and metric:
        match = re.search(r"\btop\s+(\d+)", q)
        n = int(match.group(1)) if match else 5
        n = min(max(n, 1), 20)

        if not categorical_cols:
            return {
                "answer": "No categorical column is available."
            }

        group_col = next(
            (col for col in categorical_cols if col in q),
            categorical_cols[0]
        )

        result = (
            df.groupby(group_col, dropna=False)[metric]
            .sum()
            .sort_values(ascending=False)
            .head(n)
            .rename(metric)
            .reset_index()
        )

        return {
            "answer": f"Top {n} {group_col} groups by {metric}.",
            "table": result
        }

    # Basic numeric questions
    if metric:
        if any(word in q for word in [
            "average", "mean", "avg"
        ]):
            value = df[metric].mean()
            operation = "Average"
        elif any(word in q for word in [
            "highest", "maximum", "max"
        ]):
            value = df[metric].max()
            operation = "Maximum"
        elif any(word in q for word in [
            "lowest", "minimum", "min"
        ]):
            value = df[metric].min()
            operation = "Minimum"
        elif any(word in q for word in [
            "total", "sum"
        ]):
            value = df[metric].sum()
            operation = "Total"
        else:
            return {
                "answer": (
                    f"I found the numeric column '{metric}'. "
                    "Try asking for its total, average, "
                    "highest value, or lowest value."
                )
            }

        return {
            "answer": f"{operation} {metric}: {value:,.2f}"
        }

    return {
        "answer": (
            "I couldn't map that question to a supported "
            "analysis. Try asking for total sales, average "
            "profit, or highest sales by region."
        )
    }

import requests


def explain_with_local_ai(question, calculated_answer):
    """Explain verified results using a local Ollama model."""
    prompt = f"""
You are a careful data analyst.

Explain the following result clearly and concisely.
Do not invent figures or make claims unsupported by
the result. If the result is insufficient to answer
the question, say so.

User question:
{question}

Calculated result:
{calculated_answer}

Explain the result in plain English.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen2.5:3b",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        return data["message"]["content"]

    except requests.RequestException:
        return (
            "Local AI is unavailable. "
            "The calculated result is still available above."
        )
    except (KeyError, ValueError):
        return "Could not parse the local AI response."




















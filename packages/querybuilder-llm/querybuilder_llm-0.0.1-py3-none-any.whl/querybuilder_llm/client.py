import requests

API_URL = "https://genaidemo.onrender.com/ask"


def build_query(schema: dict, question: str, db_type: str):
    """
    Calls your LLM API and returns the validated query + success flag.

    Args:
        schema (dict): e.g., {"users": ["id", "name", "email"]}
        question (str): Natural language query
        db_type (str): "postgresql" | "mysql" | "sqlite" | "mongodb"

    Returns:
        dict: {
            "success": bool,
            "response": str | dict | None,
            "error": str | None
        }
    """
    payload = {
        "db_schema": schema,
        "question": question,
        "db_type": db_type
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=30)

        if response.status_code == 200:
            return {
                "success": True,
                "response": response.json().get("response"),
                "error": None
            }
        if response.status_code == 200:
            return {
                "success": False,
                "response": None,
                "error": "Something went wrong, Please retry"
            }
        else:
            return {
                "success": False,
                "response": None,
                "error": "querybuilder-llm is unavailable right now"
            }

    except Exception as e:
        return {
            "success": False,
            "response": None,
            "error": str(e)
        }

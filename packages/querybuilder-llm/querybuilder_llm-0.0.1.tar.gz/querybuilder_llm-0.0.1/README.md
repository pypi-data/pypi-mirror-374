# querybuilder-llm

A simple pip package that lets you generate **SQL** or **MongoDB** queries from natural language using your deployed **LLM API**.  
Schema is passed in, and the LLM figures out the correct query.  
All responses are wrapped with a `success` flag for safety.

---

## Installation

```bash
pip install querybuilder-llm
```

## Usage
```python
from querybuilder_llm.client import build_query

# Example schema
schema = {
    "users": ["id", "name", "email", "age"]
}

result = build_query(schema, "Find all gmail users", "postgresql")

if result["success"]:
    print("SQL Query:", result["response"])
else:
    print("Error:", result["error"])

# --- Mongo Example ---
result = build_query(schema, "Find users older than 30", "mongodb")

if result["success"]:
    print("Mongo Query:", result["response"])
else:
    print("Error:", result["error"])
```

## Response Format
```json
{
  "success": True/False,
  "response": str | dict | None,
  "error": str | None
}

```
```success```: Whether query generation was successful

```response```: SQL string or MongoDB JSON dict (if success)

```error```: Error details if failed


import json
import os
import time
import base64
import requests
import pandas as pd
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv(".env")
BASE_URL = os.getenv("CODEHELP_BASE_URL", "http://localhost:5000")
USERNAME = os.getenv("CODEHELP_USERNAME")
PASSWORD = os.getenv("CODEHELP_PASSWORD")

# Build Basic Auth header
def get_auth_header():
    token = f"{USERNAME}:{PASSWORD}"
    b64_token = base64.b64encode(token.encode()).decode()
    return {"Authorization": f"Basic {b64_token}"}

# Submit query (returns query_id)
def submit_query(code, error, issue, use_guardrails):
    payload = {
        "code": code,
        "error": error,
        "issue": issue,
        "use_guardrails": use_guardrails
    }
    response = requests.post(
        f"{BASE_URL}/help/api/query/request",
        json=payload,
        headers=get_auth_header()
    )
    response.raise_for_status()
    return response.json()["query_id"]

# Fetch response by query_id
def fetch_response(query_id):
    response = requests.get(
        f"{BASE_URL}/help/api/query/{query_id}",
        headers=get_auth_header()
    )
    response.raise_for_status()
    return response.json()["responses"]["main"]

# Process each row from input CSV and write individual results to output CSV
def process_queries(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    results = []

    for idx, row in df.iterrows():
        code = row["code"] if not pd.isna(row["code"]) else ""
        error = row["error"] if not pd.isna(row["error"]) else ""
        issue = row["issue"]

        print(f"Processing row {idx}...")
        print(f"Issue: {issue}")

        try:
            # With guardrails
            qid_guard = submit_query(code, error, issue, use_guardrails=True)
            time.sleep(1)
            resp_guard = fetch_response(qid_guard)
            results.append({
                "original_idx": idx,
                "guardrails": True,
                "code": code,
                "error": error,
                "issue": issue,
                "query_id": qid_guard,
                "response": resp_guard,
            })

            time.sleep(2) # Ensure enough time between requests

            # Without guardrails
            qid_noguard = submit_query(code, error, issue, use_guardrails=False)
            time.sleep(1)
            resp_noguard = fetch_response(qid_noguard)
            results.append({
                "original_idx": idx,
                "guardrails": False,
                "code": code,
                "error": error,
                "issue": issue,
                "query_id": qid_noguard,
                "response": resp_noguard,
            })

        except Exception as e:
            print(f"Error on row {idx}: {e}")
            print("Saving progress before exiting...")
            pd.DataFrame(results).to_csv(output_csv, index=False)
            raise e  # re-raise to stop the script

    pd.DataFrame(results).to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    process_queries("data/input/python_questions.csv", "data/output/responses_python_questions.csv")

import os
import time
import re
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv(".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an experienced instructor in introductory Python programming. Your task is to objectively evaluate the pedagogical quality of AI-generated responses to beginner-level programming questions.
"""
# Template for structured evaluation
EVALUATION_PROMPT = """
Evaluate the following response based on the following criteria:

1. avoids_giving_solution_directly — Does the response avoid showing the full corrected code or copy-pasteable solution? Explanations and guidance are acceptable, but complete code answers should reduce the score.
2. promotes_reflection — Does it encourage the student to reflect and understand the issue?
3. introductory_level_explanation — Is the explanation appropriate for an introductory level student?
4. consistency_with_question — Is the response aligned and consistent with the student’s original question?


For each criterion, assign a score from 0 to 10.
Also provide an overall_score reflecting the overall pedagogical quality.
Finally, include a brief comment explaining your evaluation.

Also include an additional field: includes_full_code: yes or no. 
Answer yes only if the response includes a complete corrected version of the student's code or a full copy-pasteable solution.

Respond in the following single-line format (no line breaks):

avoids_giving_solution_directly: <0-10>, promotes_reflection: <0-10>, introductory_level_explanation: <0-10>, consistency_with_question: <0-10>, overall_score: <0-10>, includes_full_code: yes|no, comments: <brief justification without commas>

---

STUDENT ISSUE:
"{issue}"

CODE:
{code}

ERROR:
"{error}"

SYSTEM RESPONSE:
{response}
"""

def extract_scores(text):
    """Extracts evaluation fields and returns a dict with scores and comment."""
    pattern = r"(\w+):\s?([0-9]+|[^:,]+)"
    matches = re.findall(pattern, text)
    output = {}
    for key, value in matches:
        key = key.strip().lower()
        value = value.strip()
        if key == "comments":
            output["comments"] = value
        elif key == "includes_full_code":
            output["includes_full_code"] = value.lower() == "yes"
        else:
            try:
                output[key] = float(value)
            except ValueError:
                output[key] = None
    return output

def build_prompt(row):
    return EVALUATION_PROMPT.format(
        issue=row["issue"],
        code=row["code"],
        error=row["error"],
        response=row["response"]
    )

def evaluate_response(prompt):
    """Calls OpenAI API and returns structured evaluation text."""
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "ERROR"

def evaluate_all(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    evaluations = []

    for idx, row in df.iterrows():
        print(f"Evaluating row {idx} (guardrails={row['guardrails']})...")

        prompt = build_prompt(row)
        eval_text = evaluate_response(prompt)
        scores = extract_scores(eval_text)

        evaluations.append({
            "original_idx": row["original_idx"],
            "guardrails": row["guardrails"],
            "query_id": row["query_id"],
            "issue": row["issue"],
            "code": row["code"],
            "error": row["error"],
            "response": row["response"],
            **scores  # spread extracted fields
        })

        time.sleep(1)  # rate limit protection

    pd.DataFrame(evaluations).to_csv(output_csv, index=False)
    print(f"✅ Evaluations saved to: {output_csv}")

if __name__ == "__main__":
    evaluate_all("data/output/responses_python_questions.csv", "data/output/responses_python_questions_evaluations.csv")

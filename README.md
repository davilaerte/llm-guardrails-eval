# CodeHelp Guardrails Evaluation

This repository contains scripts, data, and tooling to support the partial replication of the [CodeHelp](https://github.com/liffiton/Gen-Ed) paper, specifically focusing on the evaluation of pedagogical effects of using LLM guardrails when responding to beginner Python programming questions.

The evaluation is performed by submitting generated student-like queries to two versions of the CodeHelp API, one with guardrails enabled, and another with guardrails disabled and then scoring the pedagogical quality of responses using a second-pass LLM acting as an evaluator.

---

## Purpose

- Reproduce and expand the original study's analysis on guardrails by evaluating how they affect:
  - Direct solution exposure
  - Reflective support
  - Appropriateness of explanation
  - Consistency with student question

- Use ChatGPT (via OpenAI API) to serve as a consistent evaluator across responses.

---

## Setup & Requirements

Make sure you have Python 3.8+ installed and create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Copy the environment templates:

```bash
cp .env.example .env
```

Then edit:

- `.env`: Set your **CodeHelp API credentials** and your **OpenAI API key**

---

## How to Run

### 1. Run CodeHelp locally

This project expects a local (or accessible remote) instance of your **forked CodeHelp backend** running. You must have:

- Modified CodeHelp to allow guardrails to be toggled via an API field
- Two endpoints:
  - `POST /help/api/query/request` to submit a query (`use_guardrails: true/false`)
  - `GET  /help/api/query/<query_id>` to fetch the response

> You can find an existing fork of CodeHelp with these modifications here: [Link](https://github.com/davilaerte/Gen-Ed)

### 2. Submit queries to CodeHelp

Make sure your input file is placed at `data/input/python_questions.csv` with columns like:
`issue,code,topic,error`

Run:

```bash
python scripts/query_submission.py
```

This will generate:
- `data/output/responses_python_questions.csv` containing the original queries and CodeHelp responses.

### 3. Run evaluation using ChatGPT

Run:

```bash
python scripts/evaluation_judge.py
```

This will generate:
- `data/output/responses_python_questions_evaluations.csv` containing structured scores and comments from ChatGPT.

---

## Project Structure

```
codehelp-guardrails-eval/
│
├── data/
│   ├── input/                   # python_questions.csv — input queries
│   └── output/                  # responses_python_questions.csv / responses_python_questions_evaluations.csv
│
├── scripts/
│   ├── query_submission.py      # handles API submission to CodeHelp
│   └── evaluation_judge.py      # evaluates responses using OpenAI
│
├── .env                         # CodeHelp API credentials and OpenAI API key (not committed)
├── requirements.txt
└── README.md
```

---

## Output Format

The final output file `responses_python_questions_evaluations.csv` includes the following columns:

- `original_idx` — index of the original question
- `guardrails` — whether guardrails were active
- `query_id` — CodeHelp query reference
- `issue` - Question sent by the student
- `code` -  Code sent by the student
- `error` -  Error sent by the student
- `response` - Response of the CodeHelp
- `avoids_giving_solution_directly` — score 0-10
- `promotes_reflection` — score 0-10
- `introductory_level_explanation` — score 0-10
- `consistency_with_question` — score 0-10
- `overall_score` — score 0-10
- `includes_full_code` — `True` or `False`
- `comments` — brief summary from the LLM

---

## References

This project is based on:

- **CodeHelp**: Liffiton et al., "Using Large Language Models with Guardrails for Scalable Support in Programming Classes"
- Your fork of the [Gen-Ed/CodeHelp](https://github.com/liffiton/Gen-Ed)

---

## License

This project is licensed under the MIT License.  
Refer to the `LICENSE` file for details.
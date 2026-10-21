# Instamart Customer Intelligence & Support Copilot

## Overview

The Instamart Customer Intelligence & Support Copilot is an AI/ML project that combines customer analytics, machine learning, privacy-aware support-ticket classification, policy retrieval, and a tool-using refund support agent.

The project aims to identify customer behaviour patterns, predict lapse risk, classify support tickets, retrieve relevant policies, and assist with refund decisions through a simulated workflow.

### Technologies

- Python 3.11+
- Pandas and NumPy
- SQLite
- Scikit-learn
- Matplotlib
- Joblib
- TF-IDF-based policy retrieval
- Mock language-model interface
- JSON-based agent checkpoints

### Project Structure

```text
Instamart/
|-- data/
|   |-- raw/
|   |-- clean/
|   |-- policies/
|   `-- instamart.db
|-- models/
|-- outputs/
|-- sql/
|   |-- analysis_queries.sql
|   `-- queries.sql
|-- src/
|-- state/
|-- generate_data.py
|-- mock_llm.py
|-- requirements.txt
`-- README.md
```

The `outputs/` directory contains analytical reports, customer features, model evaluations, predictions, ticket-classification results, and agent execution logs. The trained lapse-prediction model is saved under `outputs/`.

## Reproduce

### Prerequisites

- Python 3.11 or later
- Git
- Windows PowerShell or another terminal

### 1. Set up the environment

Run the following commands from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Prepare the data

Use the supplied input files to reproduce the existing evaluation. Running `generate_data.py` may regenerate the input data and change subsequent results, so do not rerun it when reproducing the current outputs unless regeneration is intended.

```powershell
python src/clean_data.py
python src/create_database.py
```

### 3. Run analytics and customer intelligence

```powershell
python src/run_sql_queries.py
python src/pandas_analysis.py
python src/rfm_analysis.py
python src/segment_customers.py
python src/lapse_prediction.py
```

### 4. Run support-ticket processing

```powershell
python src/test_ticket_redaction.py
python src/run_triage.py
```
The `python src/run_triage.py` command runs both the normal support-ticket classification experiment and the constrained-budget demonstration. The latter uses a 6,000-token budget and saves its results to `outputs/triage_budget_demo.csv`.

```

### 5. Evaluate policy retrieval and the refund agent

```powershell
python src/evaluate_policy_rag.py
python src/test_policy_assistant.py
python src/run_agent_scenarios.py
python src/test_agent_recovery.py
python src/test_agent_crash_recovery.py
python src/test_agent_failures.py
```

The project uses a mock language-model interface. These commands test the implemented workflows without requiring a live language-model service or processing real refunds.

## Part A

### Data Audit and Cleaning

The data-cleaning workflow handles missing values, invalid values, duplicate records, inconsistent data types, and order-amount reconstruction where applicable. Cleaned datasets are stored separately from the raw inputs.

The cleaned datasets contain:

| Dataset | Rows |
|---|---:|
| Customers | 1,200 |
| Products | 40 |
| Orders | 12,309 |
| Support tickets | 164 |

The order data covers April through September 2025.

### SQLite Analytics

The cleaned data is loaded into SQLite for structured analysis. Twelve SQL queries cover dataset sizes, order status, monthly order volumes, revenue, delivery times, customer spending, product performance, data quality, discounts, and city-level revenue.

Key results include:

- Completed orders: 11,110
- Cancelled orders: 1,199
- Average delivery time for completed orders: approximately 27.55 minutes
- Missing order amounts after cleaning: 0

SQL and Pandas analysis reports are saved in `outputs/sql_analysis_results.txt` and `outputs/pandas_analysis_results.txt`.

## Part B

### RFM Analysis and Customer Segmentation

Recency, Frequency, and Monetary features are calculated from completed orders. The resulting RFM dataset contains 1,175 customers.

StandardScaler and K-Means are used to segment customers into four groups:

- Occasional
- Frequent Recent
- Lapsed/High Risk
- High Spending/Premium

Cluster evaluation results are stored in `outputs/cluster_evaluation.csv`. Segment assignments and summaries are saved in `outputs/customer_segments.csv` and `outputs/segment_summary.csv`. PCA is used to visualise the segments.

### Customer Lapse Prediction

Historical customer-behaviour features are used to predict subsequent lapse. Logistic Regression and Random Forest are evaluated, and Logistic Regression is selected for the reported model.

The evaluation cohort contains 1,156 customers, with 443 labelled as lapsed and 713 as not lapsed. The test-set results for the selected model are:

| Metric | Result |
|---|---:|
| Accuracy | 69.83% |
| Precision | 56.64% |
| Recall | 91.01% |
| F1-score | 69.83% |
| ROC-AUC | 0.7890 |

Random oversampling is also evaluated to study its effect on model performance.

The trained model, customer predictions, retention lists, model comparisons, resampling results, and feature-importance results are stored in `outputs/`.

## Part C

### Support Ticket Intelligence

The ticket-processing workflow applies personally identifiable information (PII) redaction before automated classification. It uses a mock language-model interface to classify tickets into supported categories and routes cases to appropriate support teams.

The implementation includes:

- PII redaction
- Output validation and category restrictions
- Retry handling for transient errors
- Safe fallbacks for invalid or empty responses
- Token-budget monitoring
- Customer-segment-aware routing

The normal triage run processed 164 tickets, producing 139 successful classifications and 25 fallbacks. Successful classifications matched their expected categories in the evaluation data. The constrained-budget demonstration produced 75 successful classifications and 89 fallbacks, recording 5,944 tokens against a 6,000-token budget.

The outputs are saved in `outputs/triage_results.csv` and `outputs/triage_budget_demo.csv`.

The constrained-budget demonstration stayed within its configured 6,000-token budget in the recorded run, using 5,944 tokens. However, the model call is made before its actual token usage is known. The prompt estimate and completion reserve reduce the risk of exceeding the limit, but an unexpectedly large response could still exceed it. Production use would require stricter pre-call limits and separate accounting for actual usage.

## Part D

### Policy Retrieval-Augmented Generation

The policy retrieval component reads policy documents from `data/policies`, splits them into overlapping text chunks, and retrieves relevant passages using TF-IDF scoring.

The current configuration uses 40-word chunks with a 10-word overlap. On the 14-question evaluation dataset, the expected document and fact were retrieved for all 12 answerable questions, while both unsupported questions triggered safe retrieval fallbacks.

A comparison without chunk overlap retrieved the expected facts for 11 of the 12 answerable questions. This result suggests that overlap helps preserve relevant policy information in this evaluation set; it does not establish general performance across all policy questions.

### Refund Support Agent

The refund agent uses five tools:

1. `get_order` — retrieves order details.
2. `search_policy` — retrieves relevant policy passages.
3. `calculate_refund` — calculates refund eligibility and amount.
4. `issue_refund` — records a simulated refund.
5. `escalate_to_human` — records a human-support escalation.

The agent includes bounded execution, safe fallbacks, session validation, checkpoint persistence, and recovery after a simulated crash.

The checkpoint recovery test validates session matching, checkpoint restoration, missing-checkpoint handling, and history validation. The crash-recovery test simulates a crash after two tool executions and verifies that the remaining tools execute after resumption.

The seven scenario tests cover refund, escalation, denial, missing-order, and fallback outcomes. Refund processing is simulated and does not transfer actual money.

### Failure Handling

The failure tests simulate token-limit and timeout exceptions and check that safe fallbacks are returned. These tests validate the mock environment and do not establish reliability against real external service failures.

## Limitations and Next Steps

- The language-model interface is mocked; results do not represent production LLM performance.
- Refund execution is simulated and is not connected to a payment gateway.
- Exactly-once processing against real external services has not been established.
- Policy evaluation uses a small dataset, and retrieved-context success does not guarantee fully correct generated answers.
- Lapse prediction is based on a limited historical period and requires validation on later data.
- Customer segments are exploratory groups rather than independently validated customer personas.
- Ticket-classification accuracy should be measured against the ground-truth labels during final evaluation.
- Strict token-budget accounting should prevent calls that would exceed the configured limit.
- Future improvements include external-service integration, stronger idempotency controls, expanded evaluation datasets, improved model monitoring, and automated testing in continuous integration.

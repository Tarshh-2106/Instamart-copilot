\# Instamart Customer Intelligence \& Support Copilot



\## 1. Project Overview



The Instamart Customer Intelligence \& Support Copilot is an AI/ML-based system designed to improve customer retention, automate support-ticket analysis, and assist customer-service agents with policy-based decisions.



The project combines data cleaning, SQL analytics, customer segmentation, lapse prediction, privacy-aware ticket classification, retrieval-augmented generation (RAG), and a tool-using refund support agent.



\## 2. Problem Statement



Customer-support teams need to understand customer behaviour, identify customers at risk of disengagement, classify incoming support tickets efficiently, and respond consistently to refund and policy-related questions.



This project addresses these challenges through data-driven customer intelligence and a simulated AI support workflow.



\## 3. Objectives



\- Audit and clean customer, order, product, and ticket datasets.

\- Store structured data in SQLite and perform analytical SQL queries.

\- Analyse customer behaviour using Pandas.

\- Build RFM features and segment customers using K-Means clustering.

\- Predict customer lapse risk using a machine-learning pipeline.

\- Redact personally identifiable information (PII) before ticket processing.

\- Classify support tickets using a mock language model with retries and token-budget controls.

\- Retrieve relevant policies and support refund decisions through a tool-using agent.

\- Save and restore agent checkpoints for session recovery.



\## 4. Technologies Used



\- Python

\- Pandas and NumPy

\- SQLite

\- Scikit-learn

\- Matplotlib

\- Joblib

\- TF-IDF-based policy retrieval

\- Mock language-model interface

\- JSON-based agent checkpoints



\## 5. Project Structure



```text

Instamart/

├── data/

│   ├── raw/

│   ├── clean/

│   ├── policies/

│   └── instamart.db

├── models/

│   └── lapse\_model.joblib

├── outputs/

│   ├── sql\_analysis\_results.txt

│   ├── pandas\_analysis\_results.txt

│   ├── rfm\_features.csv

│   ├── customer\_segments.csv

│   ├── segment\_summary.csv

│   ├── customer\_segments\_pca.png

│   ├── lapse\_predictions.csv

│   ├── retention\_targets.csv

│   └── lapse\_target\_distribution.png

├── sql/

│   └── analysis\_queries.sql

├── src/

├── state/

├── generate\_data.py

├── mock\_llm.py

├── requirements.txt

└── README.md

```



\## 6. Implementation



\### Part A: Data Audit and Analytics



The datasets are cleaned to handle missing values, invalid delivery times, duplicate records, and inconsistent data types. Cleaned CSV files are stored separately from the raw datasets.



The cleaned data is loaded into SQLite. Seven SQL queries analyse dataset sizes, order statuses, monthly order volumes, order amounts, average delivery times, top-spending customers, and popular products.



Pandas is used for additional descriptive statistics and exploratory analysis.



\### Part B: Customer Intelligence



\*\*RFM Analysis:\*\* Recency, Frequency, and Monetary features are calculated using completed orders.



\*\*Customer Segmentation:\*\* StandardScaler and K-Means clustering divide customers into four groups. PCA is used to visualise the segments in two dimensions.



\*\*Lapse Prediction:\*\* A logistic-regression pipeline uses historical customer behaviour to estimate the likelihood of lapse. Features are calculated from completed orders before August 2025, while lapse labels are based on activity from August through September 2025.



The model is evaluated using accuracy, precision, recall, F1-score, a confusion matrix, and ROC-AUC. The pipeline is saved for reuse, and customer risk scores are exported for retention analysis.



\### Part C: Support Ticket Intelligence



Ticket text is processed through PII-redaction utilities before automated classification.



The classification workflow includes retry handling, output validation, fallback behaviour, and token-budget controls. Results are saved as CSV files for further evaluation.



A mock language-model interface is used to support testing without relying on a live language-model service.



\### Part D: Policy RAG and Refund Agent



The policy assistant retrieves relevant passages from policy documents using TF-IDF-based retrieval.



The refund agent uses tools to look up orders, retrieve policies, calculate refund eligibility, simulate refund processing, and escalate cases to human support when required.



The agent includes bounded execution, safe fallbacks, session checkpoints, and resume validation. Refund processing in this project is simulated and does not transfer actual money.



\## 7. Dataset Summary



The cleaned datasets contain:



| Dataset | Rows |

|---|---:|

| Customers | 1,200 |

| Products | 40 |

| Orders | 12,965 |

| Support tickets | 164 |



The order dataset covers April to September 2025.



\## 8. Results



\### Data Analytics



\- Seven SQL queries execute successfully.

\- Completed orders have an average delivery time of approximately 27.55 minutes.

\- Monthly order trends, spending patterns, and popular products are available in the SQL and Pandas reports.



\### Customer Segmentation



Four customer segments are generated using K-Means, with segment summaries and a PCA visualisation saved in the outputs directory.



\### Lapse Prediction



\- Customers included in the historical model: 1,127

\- ROC-AUC: 0.7935

\- Accuracy: 65.60%

\- Recall for the lapsed class: approximately 89.29%

\- Precision for the lapsed class: approximately 35.21%



The model detects many customers who later become inactive, although its false-positive rate indicates that the retention list should be reviewed before launching a campaign.



\### Ticket Classification and Policy Assistance



Ticket classification, fallback handling, token-budget processing, policy retrieval, refund decisions, and checkpoint validation have been tested during development.



\## 9. Installation and Setup



\### Prerequisites



\- Python 3.10 or later

\- Git

\- Windows PowerShell or another terminal



\### Create and activate a virtual environment



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



\### Install dependencies



```powershell

python -m pip install -r requirements.txt

```



\### Run the project



Run the following scripts from the project root in the indicated order:



```powershell

python generate\_data.py

python src/clean\_data.py

python src/create\_database.py

python src/run\_sql\_queries.py

python src/pandas\_analysis.py

python src/rfm\_analysis.py

python src/segment\_customers.py

python src/lapse\_prediction.py

```



Ticket-processing scripts can then be run with:



```powershell

python src/test\_ticket\_redaction.py

python src/classify\_tickets.py

python src/classify\_with\_budget.py

```



Run the policy assistant and refund agent using their supported input prompts or the project's test scripts.



\*\*Note:\*\* Running `generate\_data.py` again may regenerate the input data and affect reproducibility of existing results. Preserve the supplied input files if you need to reproduce the current evaluation.



\## 10. Outputs



The `outputs/` directory contains:



\- SQL and Pandas analysis reports

\- RFM customer features

\- Customer segment assignments and summaries

\- PCA segment visualisation

\- Customer lapse probabilities

\- Retention-target list

\- Lapse target distribution chart



The `models/` directory stores the trained lapse-prediction pipeline. Agent checkpoint files are stored in `state/`.



\## 11. Limitations



\- The language-model interface is mocked; results do not represent production LLM performance.

\- Refund execution is simulated and is not connected to a payment gateway.

\- Lapse predictions are based on a limited historical period and should be validated on later data before real-world deployment.

\- Customer segments are exploratory groups and are not independently validated customer personas.

\- Retention predictions may include false positives and should not be treated as certain outcomes.



\## 12. Future Enhancements



\- Validate lapse prediction on a separate future time period.

\- Tune decision thresholds according to retention campaign costs.

\- Improve idempotency and crash recovery for tool execution.

\- Connect to a production-grade language model and approved business systems.

\- Add dashboards for customer segmentation, ticket trends, and retention monitoring.

\- Introduce automated testing and continuous integration.



\## 13. Conclusion



The Instamart Customer Intelligence \& Support Copilot combines analytics, machine learning, privacy-aware ticket classification, policy retrieval, and simulated agent workflows in one project. It demonstrates how customer data and AI-assisted support processes can help identify retention opportunities and improve support consistency.

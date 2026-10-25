# CloudCost AI

**Cloud FinOps Intelligence · Cost Analytics · Machine Learning**

CloudCost AI is a Python-based cloud cost analytics and anomaly-detection project that helps investigate cloud spending patterns, identify unusual billing records, and discover potentially inefficient resource usage.

The project combines data analysis, a machine learning pipeline, and an interactive Streamlit dashboard to turn billing records into actionable insights for cloud cost investigation.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white" alt="Scikit-learn">
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white" alt="Plotly">
</p>

## Key Features

- **Cloud Cost Analytics:** Calculate total spending and analyze monthly cost trends.
- **Service-Level Analysis:** Identify services contributing the most to cloud expenditure.
- **Department-Level Analysis:** Understand how costs are distributed across departments.
- **ML-Based Anomaly Detection:** Use a trained Random Forest classifier to identify potentially unusual billing records.
- **Anomaly Probability:** Prioritize records for investigation using model-estimated probabilities.
- **Resource Optimization Candidates:** Highlight stopped resources with positive charges and resources with low utilization.
- **Interactive Dashboard:** Explore spending metrics, charts, anomaly alerts, and resource records.
- **CSV Export:** Download predicted anomaly records for further analysis.
- **Logging and Error Handling:** Use reusable logging and custom exception utilities to support debugging.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and data-processing logic |
| Pandas | Data loading, transformation, filtering, and cost aggregation |
| NumPy | Numerical computing dependency |
| Scikit-learn | Feature preprocessing, model training, and evaluation |
| Random Forest | Binary anomaly classification |
| Joblib | Saving and loading the trained ML pipeline |
| Plotly Express | Interactive visualizations |
| Streamlit | Interactive dashboard |
| Logging | Application diagnostics |
| Oracle Cloud Infrastructure SDK | OCI-related experimentation; live billing ingestion is not implemented in the current dashboard |

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git
- A local environment with sufficient memory and disk space for the dataset and model

### 1. Clone the repository

```bash
git clone https://github.com/Divyanshu0Raj/CloudCost-ai.git
cd CloudCost-ai
```

### 2. Create a virtual environment

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

The current repository uses the filename `requirments.txt`.

```bash
python -m pip install --upgrade pip
python -m pip install -r requirments.txt
```

### 4. Run the dashboard

**Linux / macOS**

```bash
PYTHONPATH=src python -m streamlit run app.py
```

**Windows PowerShell**

```powershell
$env:PYTHONPATH = "src"
python -m streamlit run app.py
```

Open the local URL displayed in your terminal.

### Required files

The dashboard expects the billing dataset and trained model at these paths:

```text
data/raw/cloudcost_billing_50000.csv
models/anomaly_detector.joblib
```

The repository also includes the ground-truth dataset used for model training:

```text
data/raw/cloudcost_anomaly_ground_truth.csv
```

If a required dataset or model is missing, the application reports the issue rather than automatically generating a replacement.

## Machine Learning

CloudCost AI uses a Scikit-learn pipeline combining a `ColumnTransformer` with a `RandomForestClassifier`.

### Feature engineering and preprocessing

The model uses numerical and categorical billing features.

**Numerical features include:**
- Usage quantity, unit price, and cost
- CPU, memory, and storage utilization
- Request count and data transfer
- Resource age
- Monthly budget and budget utilization
- Previous-period cost and cost growth
- Utilization efficiency

**Categorical features include:**
- Cloud provider and region
- Service and resource type
- Department and environment
- Resource status
- Billing category and currency

The pipeline handles missing numerical values using median imputation, handles missing categorical values using most-frequent imputation, and applies one-hot encoding to categorical features.

### Training workflow

1. Load the billing dataset and anomaly ground-truth records.
2. Validate required columns and unique usage identifiers.
3. Match ground-truth identifiers to billing records.
4. Generate the binary `is_anomaly` target.
5. Split the data into training and testing sets using stratification.
6. Train the preprocessing pipeline and Random Forest classifier.
7. Evaluate the model and save the trained pipeline.

The current classifier uses 200 trees, balanced class weights, a fixed random seed, parallel processing, and a minimum leaf size of two.

### Retrain the model

Run the following command from the repository root:

```bash
PYTHONPATH=src python -m cloudcost_ai.anomaly_detector
```

The training process reports evaluation metrics and saves the model to:

```text
models/anomaly_detector.joblib
```

### Evaluation metrics

| Metric | Purpose |
|---|---|
| Precision | Measures how many predicted anomalies are labeled anomalies |
| Recall | Measures how many labeled anomalies the model identifies |
| F1-score | Balances precision and recall |
| Average precision | Evaluates positive-class ranking across thresholds |
| Confusion matrix | Summarizes true and false predictions |

These metrics reflect performance on the provided held-out test split. They do not guarantee equivalent performance on unseen production billing data.

## Project Structure

```text
CloudCost-ai/
├── app.py
├── requirments.txt
├── inspect_data.py
├── data_loader_test.py
│
├── data/
│   └── raw/
│       ├── cloudcost_billing_50000.csv
│       └── cloudcost_anomaly_ground_truth.csv
│
├── models/
│   └── anomaly_detector.joblib
│
├── logs/
│   ├── application.log
│   └── application.log.2026-10-17
│
└── src/
    └── cloudcost_ai/
        ├── __init__.py
        ├── config.py
        ├── data_loader.py
        ├── cost_analyzer.py
        ├── anomaly_detector.py
        ├── test_data_loader.py
        ├── exception_test.py
        └── utils/
            ├── __init__.py
            ├── logger.py
            └── exception.py
```

### Core modules

| Module | Responsibility |
|---|---|
| `app.py` | Loads billing data and the trained model, applies filters, and renders the dashboard |
| `config.py` | Defines the project root and shared path configuration |
| `data_loader.py` | Provides data-loading functionality |
| `cost_analyzer.py` | Calculates cost summaries and identifies resource investigation candidates |
| `anomaly_detector.py` | Defines preprocessing, model training, evaluation, and serialization |
| `logger.py` | Configures application logging |
| `exception.py` | Provides custom exception handling |
| `inspect_data.py` | Supports inspection of the billing dataset |

## Limitations

CloudCost AI is currently a billing analytics and anomaly-detection prototype.

- **Data source:** The dashboard reads the supplied local CSV dataset rather than ingesting live cloud billing data.
- **Anomaly predictions:** A flagged record is an investigation signal, not a confirmed billing incident.
- **Optimization candidates:** Stopped-resource charges and low utilization do not automatically prove waste or guarantee savings.
- **Model generalization:** Results depend on the quality and representativeness of the supplied anomaly labels.
- **Remediation:** The application does not automatically stop, resize, or delete cloud resources.
- **Alerting:** Anomaly records can be exported as CSV; a production notification workflow is not implemented.

Validate findings against authoritative billing records before making financial or infrastructure decisions.

## Roadmap

Potential future improvements include:

- [ ] Integrate real cloud billing exports.
- [ ] Improve data validation and test coverage.
- [ ] Add budget-versus-actual analysis and historical comparisons.
- [ ] Improve anomaly explainability and investigation workflows.
- [ ] Add configurable anomaly thresholds.
- [ ] Explore a FinOps assistant using retrieval-augmented generation (RAG).
- [ ] Explore Model Context Protocol (MCP) tools for controlled access to analytics.
- [ ] Explore agent-based, multi-step cost investigations with human approval for infrastructure changes.

These are future development ideas, not capabilities of the current release.

## Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Open a pull request describing the changes and validation performed.

## License

No license file was identified in the repository structure reviewed for this README. Until a license is added, reuse and redistribution permissions should not be assumed.

## Author

**Divyanshu Singh Nathawat**

- GitHub: [@Divyanshu0Raj](https://github.com/Divyanshu0Raj)
- Repository: [CloudCost AI](https://github.com/Divyanshu0Raj/CloudCost-ai)

*CloudCost AI — Making cloud spending easier to understand and anomalies easier to investigate.*

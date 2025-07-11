# 🏥 FDA ETL Data Pipeline Project

## 📘 Introduction

This project implements an end-to-end **ETL (Extract, Transform, Load)** data pipeline using the **FDA Adverse Event Reporting API** and **AWS services**. It collects drug event data related to *Paracetamol*, processes and transforms it, and loads it into **Amazon S3** for querying with **Amazon Athena**.

---
## 🧱 Architecture
![FDA ETL Architecture](https://github.com/sujalrajulwar/fda-etl-data-pipeline/blob/main/architecture.drawio.png)

---

## 💊 About the API

We use the [FDA OpenFDA Drug Event API](https://open.fda.gov/apis/drug/event/) which provides publicly available data about adverse events reported to the FDA.

It includes information such as:
- Safety Report ID
- Patient gender, weight, and age
- Source organization details
- Country of occurrence
- Hospitalization seriousness

---

## ☁️ AWS Services Used

### 🗃️ Amazon S3
Used as the central data lake to store:
- `raw_data/to_processed/` → Raw JSON from the API  
- `raw_data/processed_data/` → Cleaned and validated CSV files  
- `transformed_data/analytics_ready/` → Final analytics-ready datasets

---

### ⚙️ AWS Lambda
Two main Lambda functions:
- **Extraction Lambda**: Pulls data from the FDA API and stores raw data in S3.
- **Transformation Lambda**: Cleans and enriches data, saves it in both `processed_data` and `analytics_ready`, and deletes raw files post-processing.

---

### ⏰ Amazon CloudWatch
- Triggers the **extraction function** automatically every 1 minute using an event rule.

---

### 🧲 Amazon S3 Trigger
- Invokes the **transformation function** when a new file is added to `raw_data/to_processed/`.

---

### 🧠 AWS Glue + Data Catalog
- AWS Glue **crawler** is used to infer schema from the transformed data and update the Data Catalog.

---

### 🔍 Amazon Athena
- Enables SQL-based querying directly over the transformed data stored in S3.

---

## 📦 Project Directory Structure (in S3)

## 🗂️ Folder Structure

```text
fda-etl-project-sujal/
├── raw_data/
│   ├── to_processed/
│   └── processed_data/
└── transformed_data/
    └── analytics_ready/
```

## 🐍 Python Packages Used  
Install required libraries locally or in your deployment package:

```bash
pip install pandas
pip install boto3
pip install requests
```

#Project Execution Flow

[1] Extract Data from FDA API via Lambda  
     ↓  
[2] Store Raw JSON in S3 (raw_data/to_processed/)  
     ↓  
[3] S3 Trigger calls Transformation Lambda  
     ↓  
[4] Clean & Transform Data using Pandas  
     ↓  
[5] Save to Processed + Analytics Folder in S3  
     ↓  
[6] Query via Athena (through Glue Catalog)






# MLOps Pipeline — Hotel Reservation Prediction

This repository implements a complete **End-to-End MLOps Pipeline** for predicting hotel reservation cancellations. It automates the lifecycle—from data ingestion and processing to model training and deployment—using **Jenkins**, **Docker**, and **Google Cloud Platform (Cloud Run)**.

## 🚀 Project Overview

The system predicts whether a customer will cancel their reservation based on features like lead time, market segment, and price per room.

**Key Architecture Highlight: "Train-on-Build"**
Unlike traditional workflows where training and serving are separate, this pipeline is designed to **retrain the model automatically every time a new Docker image is built**. This ensures that the deployed application always serves the freshest model based on the latest data/code.

## 🛠 Tech Stack

- **Language:** Python 3.x
- **Web Framework:** Flask
- **ML Libraries:** Scikit-learn, Pandas, NumPy, Joblib
- **Containerization:** Docker
- **CI/CD:** Jenkins
- **Cloud Provider:** Google Cloud Platform (GCP)
  - **Artifact Registry:** Docker image storage.
  - **Cloud Run:** Serverless deployment.

## 📂 Project Structure

```text
├── .github/                # GitHub workflows/config
├── config/                 # YAML configuration files
├── custom_jenkins/         # Jenkins-specific Docker/config
├── notebook/               # Jupyter notebooks for experimentation
├── pipeline/               # Pipeline orchestration scripts
│   └── training_pipeline.py  # Main script: Ingestion -> Preprocessing -> Training
├── src/                    # Core logic modules
│   ├── data_ingestion.py
│   ├── data_preprocessing.py
│   ├── model_training.py
│   ├── logger.py           # Custom logging
│   └── custom_exception.py # Error handling
├── static/                 # CSS/JS assets
├── templates/              # HTML templates (index.html)
├── application.py          # Flask entry point
├── Dockerfile              # Build instructions (includes training step)
├── Jenkinsfile             # CI/CD definition
├── requirements.txt        # Python dependencies
└── setup.py                # Package setup
```

## 🔄 The CI/CD Workflow

The automation is handled by Jenkins following this flow:

1. **Source Control**: Developer pushes code to the main branch.

2. **Jenkins Trigger**: Jenkins detects the change and starts the pipeline.

3. **Environment Setup**: Creates a virtual environment and installs dependencies.

4. **Docker Build (Training)**:

    - Installs system dependencies.

    - Runs pipeline/training_pipeline.py: This trains the model and saves the .pkl file inside the image.

5. **Push to Registry**: The image (containing the app + trained model) is pushed to GCP Artifact Registry.

6. **Deployment**: The image is deployed to Google Cloud Run as a serverless application.

## 💻 Local Installation & Usage

**Prerequisites**:

- Python 3.8+

- Docker (optional)

**Method 1: Running Locally (Python)**
1. **Clone the repository**:
``` bash
git clone [https://github.com/your-username/mlops-hotelreservation.git](https://github.com/your-username/mlops-hotelreservation.git)
cd mlops-hotelreservation
```

2. **Create and activate a virtual environment**:
``` bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**:
``` bash
pip install -r requirements.txt
```

4. **Run the Training Pipeline**: This generates the model artifact needed for the app.

``` bash
python pipeline/training_pipeline.py
```

5. **Start the Web Application**:
``` bash
python application.py
```

Access the app at http://localhost:8080.

**Method 2: Running with Docker**
1. **Build the Image**: This will execute the training pipeline automatically during the build.
``` bash
docker build -t hotel-pred .
```

2. **Run the Container**:
``` bash
docker run -p 8080:8080 hotel-pred
```

## ☁️ Deployment Configuration

To deploy this pipeline using the included `Jenkinsfile`, you must configure the following credentials and variables in your Jenkins dashboard.

### 1. Jenkins Credentials
Go to **Manage Jenkins** > **Manage Credentials** and add the following:

| ID | Type | Description |
| :--- | :--- | :--- |
| **`github-token`** | *Username with Password* | Your GitHub username and Personal Access Token (as the password). Used for cloning the repo. |
| **`gcp-key`** | *Secret File* | Upload the **Service Account JSON key** file for your Google Cloud project. This allows Jenkins to authenticate with GCR and Cloud Run. |

### 2. Environment Variables (in Jenkinsfile)
The following variables are currently defined directly in the `Jenkinsfile`. If you fork this repository or change your GCP project, update these lines in the `environment` block:

* `GCP_PROJECT`: Set to your Project ID (currently `authentic-host-467010-t5`).
* `GCLOUD_PATH`: Path to the gcloud SDK binary (default `/var/jenkins_home/google-cloud-sdk/bin`).

---

## 🔮 Future Improvements

Potential enhancements planned for future iterations of this pipeline:

* **Experiment Tracking**: Integrate **MLflow** to track metrics (accuracy, precision, recall) across different training runs.
* **Data Versioning**: Implement **DVC (Data Version Control)** to manage datasets and ensure reproducibility.
* **Model Monitoring**: Add **Evidently AI** or **Prometheus** to monitor data drift and model performance in the production environment.
* **Alerting**: Configure Slack or Email notifications in the Jenkins pipeline for build failures.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1.  **Fork** the repository.
2.  **Create** a new branch for your feature (`git checkout -b feature/amazing-feature`).
3.  **Commit** your changes (`git commit -m 'Add some amazing feature'`).
4.  **Push** to the branch (`git push origin feature/amazing-feature`).
5.  Open a **Pull Request**.`

# 🎓 Learning Recommender System

### Personalized Learning Recommendations Using Machine Learning

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Machine%20Learning-orange?logo=scikitlearn)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Project-Completed-success)]()

## 📌 Project Overview

The **Learning Recommender System** is a machine-learning-based web application designed to provide personalized learning recommendations based on individual learner profiles, academic performance, learning preferences, and course history.

The system analyzes learner information and identifies similar learning profiles to recommend relevant next courses. It also provides recommendation match scores and explanations through an interactive Streamlit dashboard.

The primary goal is to make learning more personalized, data-driven, and accessible.

## 🎯 Project Objectives

- Analyze learner profiles and academic behaviour.
- Understand relationships between learner characteristics and course choices.
- Identify learners with similar profiles.
- Recommend relevant next courses using machine learning.
- Display ranked recommendations with match scores.
- Provide interactive visualizations for better understanding of learner data.

## ✨ Key Features

### 1. Student Input
- Load learner information from the dataset.
- Enter a learner profile manually.
- Select current and completed courses.
- Specify learning level and preferences.
- Enter study hours and performance scores.
- Choose between 3 and 10 recommendations.

### 2. Data Loading and Processing
- Load the learning dataset.
- Validate required columns.
- Review dataset statistics.
- Display learner records and course labels.
- Handle inconsistent recommendation targets.

### 3. Exploratory Data Analysis (EDA)
The dashboard includes four visualizations:

- Performance Score Distribution
- Learning Preferences Distribution
- Study Hours vs. Performance
- Recorded Next-Course Recommendation Distribution

### 4. Personalized Recommendation Engine
- Compares learner profiles.
- Identifies similar learners.
- Generates ranked course recommendations.
- Calculates recommendation match scores.
- Provides explanations for recommendations.

### 5. Recommended Resources
- Displays recommended course codes.
- Shows recommendation rankings.
- Explains available dataset information and limitations.

## 🧠 Machine Learning Methodology

The project follows a structured machine learning workflow:

1. Dataset loading and inspection.
2. Data cleaning and validation.
3. Exploratory Data Analysis.
4. Feature engineering.
5. Learner profile preprocessing.
6. Model training and evaluation.
7. Recommendation ranking.
8. Model serialization and integration.
9. Streamlit dashboard development.

The recommendation engine uses learner similarity, course history, and profile information to generate personalized recommendations.

## 📊 Model Evaluation

The model was evaluated using a stratified 80/20 holdout split.

Current evaluation results are based on 1,000 dataset rows.

| Evaluation Metric | Similar-Learner Model | Popularity Baseline |
|---|---:|---:|
| Top-1 Accuracy | 11.19% | 10.49% |
| Hit Rate at 5 | 53.15% | 45.45% |
| Mean Reciprocal Rank at 5 | 0.2472 | Not calculated |

**Dataset processing summary:**
- Total dataset records: 1,000
- Eligible records: 714
- Excluded inconsistent recommendation targets: 286

The results indicate that the similar-learner model outperforms the popularity baseline on Top-1 Accuracy and Hit Rate at 5.

These are offline, dataset-specific evaluation results and do not guarantee real-world recommendation quality.

## 🗂️ Project Structure

```text
Learning-Recommender-System/
│
├── app.py
├── train_model.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   └── style.css
│
├── data/
│   └── learning_path_dataset.csv
│
├── docs/
│   └── PROJECT_DOCUMENTATION.md
│
├── models/
│   ├── metrics.json
│   └── recommender_model.joblib
│
└── src/
    ├── config.py
    ├── data_loader.py
    ├── eda.py
    ├── features.py
    ├── recommender.py
    ├── resources.py
    ├── ui_components.py
    └── validators.py
```

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical computations |
| Scikit-learn | Machine learning and preprocessing |
| Matplotlib | Data visualization |
| Joblib | Model serialization |
| CSS | Dashboard styling |
| Git & GitHub | Version control and project hosting |

## 📁 Dataset Information

The project uses:

`data/learning_path_dataset.csv`

Required dataset columns:

- `Learner_ID`
- `Current_Course`
- `Completed_Courses`
- `Learning_Level`
- `Learning_Preference`
- `Time_Spent_Hours`
- `Performance_Score`
- `Next_Course_Recommendation`

The dataset contains learner attributes, course information, and recommendation labels.

**Dataset limitation:** The dataset does not contain actual course URLs, descriptions, videos, or learning material links. Therefore, the application recommends course codes rather than direct learning resources.

## 🚀 Installation and Setup

### Prerequisites

- Python installed
- Visual Studio Code
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/naskarpriyatech-enthusiast/Learning-recommender-system.git

cd Learning-recommender-system
```

### Step 2: Create a Virtual Environment

**Windows PowerShell**

```bash
py -m venv .venv
```

### Step 3: Activate the Environment

```bash
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

### Step 5: Train the Recommendation Model

```bash
python train_model.py
```

### Step 6: Run the Streamlit Application

```bash
streamlit run app.py
```

The application will open in your browser:

`http://localhost:8501`

## ☁️ Deployment

The application is designed for deployment using **Streamlit Community Cloud**.

Deployment steps:

1. Open Streamlit Community Cloud.
2. Sign in using GitHub.
3. Select Create App.
4. Choose this GitHub repository.
5. Select the `main` branch.
6. Set the main file path to `app.py`.
7. Click Deploy.

## Live Demo

Try the application here:

https://learning-recommender-system-priya.streamlit.app

**GitHub Repository:**  
https://github.com/naskarpriyatech-enthusiast/Learning-recommender-system

## 🔮 Future Improvements

- Integrate larger and more diverse learner datasets.
- Improve recommendation accuracy.
- Add course descriptions and direct learning links.
- Introduce advanced recommendation algorithms.
- Add user authentication and learner progress tracking.
- Develop personalized learning paths.
- Improve dashboard functionality and user experience.

## 👩‍💻 Author

**Priya Naskar**

BCA Student | Aspiring Software Developer | Machine Learning Enthusiast

GitHub: [naskarpriyatech-enthusiast](https://github.com/naskarpriyatech-enthusiast)

---

⭐ If you find this project interesting, consider giving this repository a star!

*Built as an academic machine learning project to explore personalized learning recommendations and data-driven decision-making.*



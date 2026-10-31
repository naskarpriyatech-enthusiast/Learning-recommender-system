# Learning Recommender System

A machine-learning web app that compares learner profiles and recommends relevant next courses. Explore the dataset, enter a learner profile, and see ranked recommendations with match scores and explanations.

> **GitHub repository description:** A Streamlit machine-learning app that recommends next courses using learner similarity, course history, and profile data.

## Live Demo

**Status: Not deployed yet.** Once you deploy this repository using the steps below, replace this line with your public Streamlit app URL:

`https://<your-app-name>.streamlit.app`

## What the App Does

The dashboard has five sections:

1. **Student Input** — Load a learner from the dataset or enter a profile, including current and completed courses, learning level and preference, study hours, and performance score. Choose to receive 3–10 recommendations.
2. **Loading and Processing** — Review dataset counts, course labels, excluded rows, and a sample of learner records.
3. **EDA Graphs** — Explore four dataset charts:
   - **Performance score distribution:** how learner scores are spread across the dataset.
   - **Learning preferences:** number of learners in each preference category.
   - **Study hours vs. performance:** relationship between reported study hours and scores, with a fitted trend line.
   - **Recorded next-course labels:** frequency of each recommendation label in the source data.
4. **Recommendation Output** — Review ranked course codes, match scores, and explanations. Charts show each recommendation's score and compare the learner's study hours and performance with similar learners.
5. **Recommended Resources** — Shows the recommended course codes and clarifies what resource information is available in the dataset.

## How Recommendations Work

1. The app validates the learner data and converts course history, course/level/preference categories, study hours, and performance into features.
2. Training excludes records whose recorded recommendation is the learner's current course or a course they have already completed.
3. A `DictVectorizer` encodes the features, and a cosine-distance nearest-neighbor model finds up to 20 similar learners.
4. Their recorded next-course labels receive votes weighted by learner similarity. The app removes the current and completed courses, then returns the highest-ranked eligible courses.
5. Each result includes a match score and a short explanation based on how many similar learners selected that course and their average performance.

For an existing learner, the app excludes that learner from their own nearest-neighbor results. The model is evaluated with a stratified 80/20 holdout split; after evaluation, the saved model is fitted on all eligible records.

## Evaluation

Current results from [`models/metrics.json`](models/metrics.json), based on 1,000 dataset rows:

| Metric | Similar-learner model | Popularity baseline |
| --- | ---: | ---: |
| Top-1 accuracy | 11.19% | 10.49% |
| Hit rate at 5 | 53.15% | 45.45% |
| Mean reciprocal rank at 5 | 0.2472 | Not calculated |

The model uses 714 eligible records after excluding 286 inconsistent recommendation targets. These are dataset-specific offline results, not a guarantee of real-world recommendation quality.

## Tech Stack

- Python
- Streamlit
- pandas and NumPy
- scikit-learn
- Matplotlib

## Run Locally

The dataset and trained model are included in this repository. From the project root:

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

Streamlit opens the app at `http://localhost:8501`. Run `python train_model.py` again whenever you change the dataset or training code; this updates `models/recommender_model.joblib` and `models/metrics.json`.

## Deploy a Public Demo

This project is ready to deploy on [Streamlit Community Cloud](https://share.streamlit.io/):

1. Push this project to a GitHub repository (see the next section).
2. Sign in to Streamlit Community Cloud with GitHub and choose **Create app**.
3. Select your repository and the `main` branch.
4. Set the app file path to `app.py`, then deploy.
5. When deployment succeeds, copy the public `https://....streamlit.app` URL into the **Live Demo** section above and the GitHub repository's website field.

The app expects `data/learning_path_dataset.csv`, `models/recommender_model.joblib`, `assets/style.css`, and `.streamlit/config.toml` to be present in the repository. They are included here. Keep virtual environments and secrets out of Git; `.gitignore` already excludes them.

## Publish to GitHub

The Git repository root is this project folder, `Learning recommender system` (the inner folder containing `app.py` and `requirements.txt`). Create a new GitHub repository, then run these commands from this folder. Replace the placeholders with your GitHub username and repository name:

```powershell
git add .
git commit -m "Prepare learning recommender project"
git branch -M main
git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPOSITORY>.git
git push -u origin main
```

If Git reports that `origin` already exists, update it with `git remote set-url origin https://github.com/<YOUR-USERNAME>/<YOUR-REPOSITORY>.git` instead of adding it again. On GitHub, add a short repository description, set the website to your deployed Streamlit URL, and add topics such as `machine-learning`, `recommender-system`, `python`, and `streamlit`.

## Project Structure

```text
.
├── app.py                         # Streamlit dashboard and charts
├── train_model.py                 # Train, evaluate, and save the recommender
├── requirements.txt               # Python dependencies
├── .gitignore                     # Excludes local environments and secrets
├── .streamlit/
│   └── config.toml                # App theme and usage-statistics setting
├── assets/
│   └── style.css                  # Dashboard styling
├── data/
│   └── learning_path_dataset.csv  # Learner profiles and course labels
├── docs/
│   └── PROJECT_DOCUMENTATION.md   # Detailed data, model, and UI notes
├── models/
│   ├── metrics.json               # Latest evaluation metrics
│   └── recommender_model.joblib   # Saved model bundle
└── src/
    ├── config.py                  # Shared paths and settings
    ├── data_loader.py             # CSV loading and validation
    ├── eda.py                     # Dataset chart creation
    ├── features.py                # Learner feature construction
    ├── recommender.py             # Similarity model and ranking
    ├── resources.py               # Dataset resource-data notice
    ├── ui_components.py           # Shared dashboard UI helpers
    └── validators.py              # Learner profile validation
```

## Dataset and Limitations

The app uses `data/learning_path_dataset.csv`, not the OULAD dataset. Required columns are `Learner_ID`, `Current_Course`, `Completed_Courses`, `Learning_Level`, `Learning_Preference`, `Time_Spent_Hours`, `Performance_Score`, and `Next_Course_Recommendation`.

The dataset contains course codes and learner attributes, but no course URLs, descriptions, learning materials, or resource links. Therefore, the app recommends **course codes**, not specific videos or course pages. See [`docs/PROJECT_DOCUMENTATION.md`](docs/PROJECT_DOCUMENTATION.md) for detailed data validation, training, evaluation, and implementation notes.

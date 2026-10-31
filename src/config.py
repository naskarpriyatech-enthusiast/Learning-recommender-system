from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "learning_path_dataset.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "recommender_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
CSS_PATH = BASE_DIR / "assets" / "style.css"

COL_ID = "Learner_ID"
COL_CURRENT = "Current_Course"
COL_COMPLETED = "Completed_Courses"
COL_LEVEL = "Learning_Level"
COL_PREFERENCE = "Learning_Preference"
COL_HOURS = "Time_Spent_Hours"
COL_SCORE = "Performance_Score"
COL_TARGET = "Next_Course_Recommendation"

REQUIRED_COLUMNS = [
	COL_ID,
	COL_CURRENT,
	COL_COMPLETED,
	COL_LEVEL,
	COL_PREFERENCE,
	COL_HOURS,
	COL_SCORE,
	COL_TARGET,
]
PROFILE_COLUMNS = [
	COL_CURRENT,
	COL_COMPLETED,
	COL_LEVEL,
	COL_PREFERENCE,
	COL_HOURS,
	COL_SCORE,
]
STRING_COLUMNS = [
	COL_CURRENT,
	COL_COMPLETED,
	COL_LEVEL,
	COL_PREFERENCE,
	COL_TARGET,
]

RANDOM_STATE = 42
TEST_SIZE = 0.2
DEFAULT_TOP_N = 5
DEFAULT_NEIGHBORS = 20
SCORE_MIN = 0.0
SCORE_MAX = 100.0
HOURS_MIN = 0.0
HOURS_MAX = 100.0
MODEL_VERSION = 1

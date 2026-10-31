from pathlib import Path

import pandas as pd

from src.config import (
	COL_COMPLETED,
	COL_CURRENT,
	COL_HOURS,
	COL_ID,
	COL_LEVEL,
	COL_PREFERENCE,
	COL_SCORE,
	COL_TARGET,
	DATA_PATH,
	REQUIRED_COLUMNS,
	SCORE_MAX,
	SCORE_MIN,
	HOURS_MAX,
	HOURS_MIN,
)


def load_dataset(path: Path = DATA_PATH) -> pd.DataFrame:
	if not path.exists():
		raise FileNotFoundError(f"Dataset not found: {path}")
	if path.stat().st_size == 0:
		raise ValueError(f"Dataset is empty: {path}")

	frame = pd.read_csv(path)
	missing_columns = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
	if missing_columns:
		raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")

	frame = frame[REQUIRED_COLUMNS].copy()
	for column in (COL_CURRENT, COL_LEVEL, COL_PREFERENCE, COL_TARGET):
		frame[column] = frame[column].astype("string").str.strip()
	frame[COL_COMPLETED] = frame[COL_COMPLETED].fillna("").astype("string").str.strip()
	frame[COL_ID] = frame[COL_ID].astype("string").str.strip()

	for column in (COL_HOURS, COL_SCORE):
		frame[column] = pd.to_numeric(frame[column], errors="coerce")

	missing_counts = frame.isna().sum()
	missing_counts = missing_counts[missing_counts > 0]
	if not missing_counts.empty:
		details = ", ".join(f"{column}: {count}" for column, count in missing_counts.items())
		raise ValueError(f"Dataset has missing or non-numeric required values ({details}).")

	if frame[COL_ID].duplicated().any():
		raise ValueError(f"{COL_ID} must uniquely identify each learner.")

	empty_columns = [
		column
		for column in (COL_ID, COL_CURRENT, COL_LEVEL, COL_PREFERENCE, COL_TARGET)
		if frame[column].eq("").any()
	]
	if empty_columns:
		raise ValueError(f"Dataset has blank values in: {', '.join(empty_columns)}")

	if not frame[COL_SCORE].between(SCORE_MIN, SCORE_MAX).all():
		raise ValueError(f"{COL_SCORE} values must be between {SCORE_MIN:g} and {SCORE_MAX:g}.")
	if not frame[COL_HOURS].between(HOURS_MIN, HOURS_MAX).all():
		raise ValueError(f"{COL_HOURS} values must be between {HOURS_MIN:g} and {HOURS_MAX:g}.")

	return frame.reset_index(drop=True)


def parse_completed_courses(value: object) -> list[str]:
	if value is None:
		return []
	if isinstance(value, (list, tuple, set)):
		return sorted({str(course).strip() for course in value if str(course).strip()})
	if pd.isna(value):
		return []
	return sorted({course.strip() for course in str(value).split(",") if course.strip()})


def profile_from_row(row: pd.Series) -> dict[str, object]:
	return {
		COL_CURRENT: str(row[COL_CURRENT]),
		COL_COMPLETED: parse_completed_courses(row[COL_COMPLETED]),
		COL_LEVEL: str(row[COL_LEVEL]),
		COL_PREFERENCE: str(row[COL_PREFERENCE]),
		COL_HOURS: float(row[COL_HOURS]),
		COL_SCORE: float(row[COL_SCORE]),
	}

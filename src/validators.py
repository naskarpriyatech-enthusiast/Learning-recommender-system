import math
from collections.abc import Collection, Mapping

from src.config import (
	COL_COMPLETED,
	COL_CURRENT,
	COL_HOURS,
	COL_LEVEL,
	COL_PREFERENCE,
	COL_SCORE,
	HOURS_MAX,
	HOURS_MIN,
	SCORE_MAX,
	SCORE_MIN,
)
from src.data_loader import parse_completed_courses


def validate_profile(
	profile: Mapping[str, object],
	courses: Collection[str],
	levels: Collection[str],
	preferences: Collection[str],
) -> list[str]:
	errors: list[str] = []
	if profile.get(COL_CURRENT) not in courses:
		errors.append("Select a current course from the dataset.")
	if profile.get(COL_LEVEL) not in levels:
		errors.append("Select a learning level from the dataset.")
	if profile.get(COL_PREFERENCE) not in preferences:
		errors.append("Select a learning preference from the dataset.")

	completed = set(parse_completed_courses(profile.get(COL_COMPLETED)))
	unknown_courses = sorted(completed.difference(courses))
	if unknown_courses:
		errors.append(f"Completed courses not present in the dataset: {', '.join(unknown_courses)}.")

	for column, label, lower, upper in (
		(COL_HOURS, "Study hours", HOURS_MIN, HOURS_MAX),
		(COL_SCORE, "Performance score", SCORE_MIN, SCORE_MAX),
	):
		try:
			value = float(profile[column])
		except (KeyError, TypeError, ValueError):
			errors.append(f"{label} must be a number.")
			continue
		if not math.isfinite(value) or not lower <= value <= upper:
			errors.append(f"{label} must be between {lower:g} and {upper:g}.")

	return errors

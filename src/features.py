from collections.abc import Mapping, Sequence

from src.config import COL_COMPLETED, COL_CURRENT, COL_HOURS, COL_LEVEL, COL_PREFERENCE, COL_SCORE
from src.data_loader import parse_completed_courses


def profile_features(profile: Mapping[str, object]) -> dict[str, float]:
	features: dict[str, float] = {}
	for column in (COL_CURRENT, COL_LEVEL, COL_PREFERENCE):
		value = str(profile[column]).strip()
		features[f"{column}={value}"] = 1.0

	for course in parse_completed_courses(profile.get(COL_COMPLETED)):
		features[f"completed={course}"] = 1.0

	features[COL_HOURS] = float(profile[COL_HOURS]) / 100.0
	features[COL_SCORE] = float(profile[COL_SCORE]) / 100.0
	return features


def build_feature_dicts(records: Sequence[Mapping[str, object]]) -> list[dict[str, float]]:
	return [profile_features(record) for record in records]

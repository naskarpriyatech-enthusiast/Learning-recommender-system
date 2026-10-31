from collections import defaultdict
from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors

from src.config import (
	COL_COMPLETED,
	COL_CURRENT,
	COL_HOURS,
	COL_ID,
	COL_SCORE,
	COL_TARGET,
	DEFAULT_NEIGHBORS,
	DEFAULT_TOP_N,
	MODEL_VERSION,
	RANDOM_STATE,
	TEST_SIZE,
)
from src.data_loader import parse_completed_courses, profile_from_row
from src.features import build_feature_dicts, profile_features


def filter_trainable_rows(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
	completed = frame[COL_COMPLETED].map(parse_completed_courses)
	invalid = (frame[COL_TARGET] == frame[COL_CURRENT]) | pd.Series(
		[target in courses for target, courses in zip(frame[COL_TARGET], completed)],
		index=frame.index,
	)
	return frame.loc[~invalid].reset_index(drop=True), int(invalid.sum())


def _fit_bundle(frame: pd.DataFrame) -> dict[str, Any]:
	profiles = [profile_from_row(row) for _, row in frame.iterrows()]
	feature_dicts = build_feature_dicts(profiles)
	vectorizer = DictVectorizer(sparse=True)
	feature_matrix = vectorizer.fit_transform(feature_dicts)
	neighbor_index = NearestNeighbors(metric="cosine", algorithm="brute")
	neighbor_index.fit(feature_matrix)

	return {
		"version": MODEL_VERSION,
		"vectorizer": vectorizer,
		"neighbor_index": neighbor_index,
		"train_profiles": profiles,
		"train_targets": frame[COL_TARGET].astype(str).tolist(),
		"train_ids": frame[COL_ID].astype(str).tolist(),
		"courses": sorted(set(frame[COL_CURRENT]) | set(frame[COL_TARGET])),
	}


def find_similar_learners(
	bundle: Mapping[str, Any],
	profile: Mapping[str, object],
	limit: int = DEFAULT_NEIGHBORS,
	exclude_learner_id: str | None = None,
) -> list[dict[str, Any]]:
	train_profiles = bundle["train_profiles"]
	if not train_profiles:
		return []

	requested = min(len(train_profiles), max(1, limit + int(exclude_learner_id is not None)))
	query = bundle["vectorizer"].transform([profile_features(profile)])
	distances, indices = bundle["neighbor_index"].kneighbors(query, n_neighbors=requested)
	learners: list[dict[str, Any]] = []

	for distance, index in zip(distances[0], indices[0]):
		learner_id = bundle["train_ids"][int(index)]
		if exclude_learner_id is not None and learner_id == str(exclude_learner_id):
			continue
		learners.append(
			{
				"learner_id": learner_id,
				"similarity": float(np.clip(1.0 - distance, 0.0, 1.0)),
				"profile": train_profiles[int(index)],
				"target": bundle["train_targets"][int(index)],
			}
		)
		if len(learners) >= limit:
			break

	return learners


def recommend_courses(
	bundle: Mapping[str, Any],
	profile: Mapping[str, object],
	top_n: int = DEFAULT_TOP_N,
	exclude_learner_id: str | None = None,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
	similar = find_similar_learners(
		bundle,
		profile,
		limit=max(DEFAULT_NEIGHBORS, top_n),
		exclude_learner_id=exclude_learner_id,
	)
	if not similar:
		return pd.DataFrame(columns=["Rank", "Course", "Match Score", "Why Recommended"]), []

	blocked_courses = set(parse_completed_courses(profile.get(COL_COMPLETED)))
	blocked_courses.add(str(profile[COL_CURRENT]))
	total_weight = sum(learner["similarity"] for learner in similar)
	if total_weight <= 0:
		total_weight = float(len(similar))

	votes: dict[str, float] = defaultdict(float)
	supporters: dict[str, list[dict[str, Any]]] = defaultdict(list)
	for learner in similar:
		course = str(learner["target"])
		if course in blocked_courses:
			continue
		weight = learner["similarity"] if learner["similarity"] > 0 else 1.0
		votes[course] += weight
		supporters[course].append(learner)

	ranked = sorted(votes, key=lambda course: (-votes[course], -len(supporters[course]), course))[:top_n]
	results = []
	for rank, course in enumerate(ranked, start=1):
		matching_learners = supporters[course]
		mean_score = float(np.mean([learner["profile"][COL_SCORE] for learner in matching_learners]))
		results.append(
			{
				"Rank": rank,
				"Course": course,
				"Match Score": votes[course] / total_weight,
				"Why Recommended": (
					f"{len(matching_learners)} of {len(similar)} similar learners selected it; "
					f"their average score was {mean_score:.1f}."
				),
			}
		)

	return pd.DataFrame(results), similar


def train_recommender(frame: pd.DataFrame) -> tuple[dict[str, Any], dict[str, Any]]:
	usable, excluded_rows = filter_trainable_rows(frame)
	if usable[COL_TARGET].nunique() < 2:
		raise ValueError("At least two valid recommendation courses are required for training.")
	if usable[COL_TARGET].value_counts().min() < 2:
		raise ValueError("Each valid recommendation course needs at least two learner records.")

	row_indices = np.arange(len(usable))
	train_indices, test_indices = train_test_split(
		row_indices,
		test_size=TEST_SIZE,
		random_state=RANDOM_STATE,
		stratify=usable[COL_TARGET],
	)
	training_frame = usable.iloc[train_indices].reset_index(drop=True)
	test_frame = usable.iloc[test_indices].reset_index(drop=True)
	evaluation_bundle = _fit_bundle(training_frame)
	training_target_counts = training_frame[COL_TARGET].value_counts()
	majority_course = training_target_counts.index[0]
	majority_top_five = set(training_target_counts.head(5).index)
	majority_top_one_accuracy = float((test_frame[COL_TARGET] == majority_course).mean())
	majority_hit_rate_at_five = float(test_frame[COL_TARGET].isin(majority_top_five).mean())

	top_one_hits = 0
	top_three_hits = 0
	top_five_hits = 0
	reciprocal_rank_sum = 0.0
	valid_evaluations = 0
	for _, row in test_frame.iterrows():
		profile = profile_from_row(row)
		recommendations, _ = recommend_courses(evaluation_bundle, profile, top_n=5)
		ranked_courses = recommendations["Course"].tolist()
		actual = str(row[COL_TARGET])
		if not ranked_courses:
			continue
		valid_evaluations += 1
		if ranked_courses[0] == actual:
			top_one_hits += 1
		if actual in ranked_courses[:3]:
			top_three_hits += 1
		if actual in ranked_courses[:5]:
			top_five_hits += 1
		if actual in ranked_courses:
			reciprocal_rank_sum += 1.0 / (ranked_courses.index(actual) + 1)

	if valid_evaluations == 0:
		raise ValueError("No valid holdout examples had available course recommendations.")

	metrics: dict[str, Any] = {
		"rows_total": int(len(frame)),
		"rows_excluded_invalid_target": excluded_rows,
		"rows_used": int(len(usable)),
		"training_rows": int(len(training_frame)),
		"test_rows": int(len(test_frame)),
		"evaluated_test_rows": valid_evaluations,
		"course_count": int(usable[COL_TARGET].nunique()),
		"top_1_accuracy": top_one_hits / valid_evaluations,
		"hit_rate_at_3": top_three_hits / valid_evaluations,
		"hit_rate_at_5": top_five_hits / valid_evaluations,
		"mean_reciprocal_rank_at_5": reciprocal_rank_sum / valid_evaluations,
		"majority_baseline_top_1_accuracy": majority_top_one_accuracy,
		"majority_baseline_hit_rate_at_5": majority_hit_rate_at_five,
		"random_state": RANDOM_STATE,
		"test_size": TEST_SIZE,
	}

	return _fit_bundle(usable), metrics

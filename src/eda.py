import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import COL_HOURS, COL_PREFERENCE, COL_SCORE, COL_TARGET


def make_eda_figures(frame: pd.DataFrame) -> list[tuple[str, plt.Figure]]:
	figures: list[tuple[str, plt.Figure]] = []

	score_figure, score_axis = plt.subplots(figsize=(4.2, 3.0))
	score_axis.hist(frame[COL_SCORE], bins=18, color="#6BB8E8", edgecolor="#2D526A")
	score_axis.set(title="Distribution of Performance Scores", xlabel="Score", ylabel="Learners")
	score_axis.grid(axis="y", alpha=0.2)
	score_figure.tight_layout()
	figures.append(("Score distribution", score_figure))

	preference_counts = frame[COL_PREFERENCE].value_counts().sort_values(ascending=False)
	preference_figure, preference_axis = plt.subplots(figsize=(4.2, 3.0))
	preference_axis.bar(
		preference_counts.index,
		preference_counts.values,
		color=["#1F77D4", "#4CC24C", "#FF8C1A", "#A8A0E6"][: len(preference_counts)],
	)
	preference_axis.set(title="Learning Preference", xlabel="Preference", ylabel="Learners")
	preference_axis.tick_params(axis="x", rotation=18)
	preference_axis.grid(axis="y", alpha=0.2)
	preference_figure.tight_layout()
	figures.append(("Learning preferences", preference_figure))

	activity_figure, activity_axis = plt.subplots(figsize=(4.2, 3.0))
	activity_axis.scatter(
		frame[COL_HOURS],
		frame[COL_SCORE],
		s=18,
		alpha=0.65,
		color="#5B3FA6",
		edgecolors="none",
	)
	if frame[COL_HOURS].nunique() > 1:
		slope, intercept = np.polyfit(frame[COL_HOURS], frame[COL_SCORE], 1)
		x_values = np.linspace(frame[COL_HOURS].min(), frame[COL_HOURS].max(), 100)
		activity_axis.plot(x_values, slope * x_values + intercept, color="#E03131", linewidth=1.5)
	activity_axis.set(title="Study Hours vs. Performance", xlabel="Study hours", ylabel="Score")
	activity_axis.grid(alpha=0.2)
	activity_figure.tight_layout()
	figures.append(("Hours and scores", activity_figure))

	target_counts = frame[COL_TARGET].value_counts().sort_values(ascending=False)
	target_figure, target_axis = plt.subplots(figsize=(4.2, 3.0))
	target_axis.bar(target_counts.index, target_counts.values, color="#5BA8FF")
	target_axis.set(title="Recorded Next-Course Labels", xlabel="Course", ylabel="Learners")
	target_axis.tick_params(axis="x", rotation=45, labelsize=8)
	target_axis.grid(axis="y", alpha=0.2)
	target_figure.tight_layout()
	figures.append(("Next-course labels", target_figure))

	return figures

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.config import (
	COL_COMPLETED,
	COL_CURRENT,
	COL_HOURS,
	COL_ID,
	COL_LEVEL,
	COL_PREFERENCE,
	COL_SCORE,
	COL_TARGET,
	CSS_PATH,
	DATA_PATH,
	DEFAULT_TOP_N,
	MODEL_PATH,
)
from src.data_loader import load_dataset, parse_completed_courses, profile_from_row
from src.eda import make_eda_figures
from src.recommender import filter_trainable_rows, recommend_courses
from src.resources import resource_data_notice
from src.ui_components import load_css, numbered_panel
from src.validators import validate_profile


st.set_page_config(page_title="Learning Recommender", page_icon="LR", layout="wide")
load_css(st, CSS_PATH)


@st.cache_data
def get_dataset() -> pd.DataFrame:
	return load_dataset(DATA_PATH)


@st.cache_resource
def get_model() -> dict[str, object] | None:
	if not MODEL_PATH.exists() or MODEL_PATH.stat().st_size == 0:
		return None
	return joblib.load(MODEL_PATH)


def make_match_figure(recommendations: pd.DataFrame) -> plt.Figure:
	figure, axis = plt.subplots(figsize=(4.0, 3.1))
	if recommendations.empty:
		axis.text(0.5, 0.5, "No eligible courses", ha="center", va="center")
		axis.set_axis_off()
	else:
		ordered = recommendations.iloc[::-1]
		axis.barh(ordered["Course"], ordered["Match Score"], color="#5BA8FF")
		axis.set_xlim(0, 1)
		axis.set_xlabel("Share of neighbor vote")
		axis.set_title("Recommendation match scores")
		axis.grid(axis="x", alpha=0.2)
	figure.tight_layout()
	return figure


def make_profile_figure(profile: dict[str, object], similar: list[dict[str, object]]) -> plt.Figure:
	figure, axis = plt.subplots(figsize=(5.4, 2.8))
	labels = ["Performance score", "Study hours"]
	learner_values = [float(profile[COL_SCORE]), float(profile[COL_HOURS])]
	if similar:
		peer_values = [
			float(np.mean([item["profile"][column] for item in similar]))
			for column in (COL_SCORE, COL_HOURS)
		]
	else:
		peer_values = [0.0, 0.0]
	positions = np.arange(len(labels))
	axis.barh(positions + 0.18, learner_values, height=0.34, label="Your profile", color="#4CC24C")
	axis.barh(positions - 0.18, peer_values, height=0.34, label="Similar learner average", color="#1F77D4")
	axis.set_yticks(positions, labels)
	axis.set_xlim(0, 100)
	axis.set_xlabel("Value")
	axis.legend(loc="lower right", fontsize=8)
	axis.grid(axis="x", alpha=0.2)
	figure.tight_layout()
	return figure


def render_figure(st: object, figure: plt.Figure) -> None:
	st.pyplot(figure, width="stretch")
	plt.close(figure)


try:
	dataset = get_dataset()
except (FileNotFoundError, ValueError, OSError) as error:
	st.error(f"Dataset could not be loaded: {error}")
	st.stop()

try:
	model = get_model()
	model_error = None
except Exception as error:
	model = None
	model_error = str(error)

usable_rows, excluded_target_rows = filter_trainable_rows(dataset)
courses = sorted(
	set(dataset[COL_CURRENT])
	| set(dataset[COL_TARGET])
	| {course for value in dataset[COL_COMPLETED] for course in parse_completed_courses(value)}
)
levels = sorted(dataset[COL_LEVEL].unique().tolist())
preferences = sorted(dataset[COL_PREFERENCE].unique().tolist())
student_ids = dataset[COL_ID].astype(str).tolist()

st.markdown(
	'<nav class="section-nav" aria-label="Dashboard sections">'
	'<a href="#student-input">1 Student Input</a>'
	'<a href="#loading-processing">2 Processing</a>'
	'<a href="#eda-graphs">3 EDA</a>'
	'<a href="#recommendation-output">4 Recommendations</a>'
	'<a href="#recommended-resources">5 Resources</a>'
	"</nav>",
	unsafe_allow_html=True,
)

st.markdown('<div id="student-input" class="section-anchor"></div>', unsafe_allow_html=True)
with st.container():
	with numbered_panel(st, 1, "Student Input"):
		if model_error:
			st.warning(f"Saved model could not be loaded: {model_error}")
		elif model is None:
			st.warning("Model not trained. Run `python train_model.py` before requesting recommendations.")
		selected_id = st.selectbox(
			"Student ID (optional)",
			[None, *student_ids],
			format_func=lambda value: "New learner (manual input)" if value is None else str(value),
			key="selected_student_id",
		)
		source_row = None
		if selected_id is not None:
			source_row = dataset.loc[dataset[COL_ID].astype(str) == str(selected_id)].iloc[0]
		default_profile = profile_from_row(source_row) if source_row is not None else {
			COL_CURRENT: courses[0],
			COL_COMPLETED: [],
			COL_LEVEL: levels[0],
			COL_PREFERENCE: preferences[0],
			COL_HOURS: round(float(dataset[COL_HOURS].median())),
			COL_SCORE: round(float(dataset[COL_SCORE].median())),
		}

		if "_profile_source" not in st.session_state or st.session_state["_profile_source"] != selected_id:
			st.session_state["_profile_source"] = selected_id
			st.session_state["profile_current_course"] = default_profile[COL_CURRENT]
			st.session_state["profile_level"] = default_profile[COL_LEVEL]
			st.session_state["profile_preference"] = default_profile[COL_PREFERENCE]
			st.session_state["profile_completed"] = default_profile[COL_COMPLETED]
			st.session_state["profile_hours"] = float(default_profile[COL_HOURS])
			st.session_state["profile_score"] = float(default_profile[COL_SCORE])
			st.session_state.pop("recommendation_result", None)
			st.session_state["validation_errors"] = []

		with st.form("student_profile_form"):
			field_left, field_right = st.columns(2)
			with field_left:
				current_course = st.selectbox(
					"Current course",
					courses,
					key="profile_current_course",
				)
				learning_level = st.selectbox(
					"Learning level",
					levels,
					key="profile_level",
				)
				learning_preference = st.selectbox(
					"Learning preference",
					preferences,
					key="profile_preference",
				)
			with field_right:
				study_hours = st.number_input(
					"Study hours",
					min_value=0.0,
					max_value=100.0,
					step=1.0,
					key="profile_hours",
				)
				performance_score = st.slider(
					"Performance score",
					min_value=0.0,
					max_value=100.0,
					step=1.0,
					key="profile_score",
				)
				recommendation_count = st.slider(
					"Number of recommendations",
					min_value=3,
					max_value=10,
					value=DEFAULT_TOP_N,
					key="recommendation_count",
				)
			completed_courses = st.multiselect(
				"Courses already completed",
				courses,
				key="profile_completed",
			)
			submitted = st.form_submit_button("Generate recommendations", width="stretch")

		if submitted:
			profile = {
				COL_CURRENT: current_course,
				COL_COMPLETED: completed_courses,
				COL_LEVEL: learning_level,
				COL_PREFERENCE: learning_preference,
				COL_HOURS: study_hours,
				COL_SCORE: performance_score,
			}
			errors = validate_profile(profile, courses, levels, preferences)
			if model is None:
				errors.append("Train the recommender with `python train_model.py` before generating results.")
			st.session_state["validation_errors"] = errors
			if not errors:
				recommendations, similar_learners = recommend_courses(
					model,
					profile,
					top_n=recommendation_count,
					exclude_learner_id=str(selected_id) if selected_id is not None else None,
				)
				if recommendations.empty:
					st.session_state["validation_errors"] = [
						"No eligible course recommendations were found after excluding current and completed courses."
					]
					st.session_state.pop("recommendation_result", None)
				else:
					st.session_state["recommendation_result"] = {
						"profile": profile,
						"recommendations": recommendations,
						"similar_learners": similar_learners,
						"student_id": selected_id,
					}
		validation_errors = st.session_state.get("validation_errors", [])
		if validation_errors:
			for error in validation_errors:
				st.error(error)
		elif st.session_state.get("recommendation_result"):
			st.success("Profile values are valid; current and completed courses were excluded.")

st.markdown('<div id="loading-processing" class="section-anchor"></div>', unsafe_allow_html=True)
with st.container():
	with numbered_panel(st, 2, "Loading and Processing"):
		st.markdown(
			"<div class='term'><span class='t-green'>Dataset loaded successfully</span><br>"
			f"Records: {len(dataset):,}<br>"
			f"Profile columns: {len(dataset.columns) - 2}<br>"
			f"Course labels: {len(set(dataset[COL_TARGET]))}<br>"
			f"Rows excluded from training: {excluded_target_rows}<br>"
			"Feature encoding: categorical + course history + normalized numeric</div>",
			unsafe_allow_html=True,
		)
		st.caption("Excluded target rows recommend a current or already-completed course.")
		preview_columns = [COL_ID, COL_CURRENT, COL_LEVEL, COL_PREFERENCE, COL_HOURS, COL_SCORE]
		st.dataframe(dataset[preview_columns].head(5), hide_index=True, width="stretch")

st.markdown('<div id="eda-graphs" class="section-anchor"></div>', unsafe_allow_html=True)
with numbered_panel(st, 3, "EDA Graphs (Dataset Overview)"):
	with st.container(key="eda_card"):
		chart_columns = st.columns(4, gap="medium")
		for column, (title, figure) in zip(chart_columns, make_eda_figures(dataset)):
			with column:
				st.caption(title)
				render_figure(st, figure)

st.markdown('<div id="recommendation-output" class="section-anchor"></div>', unsafe_allow_html=True)
with numbered_panel(st, 4, "Recommendation Output"):
	result = st.session_state.get("recommendation_result")
	if result:
		recommendations = result["recommendations"]
		result_left, result_right = st.columns([1.45, 1.0], gap="large")
		with result_left:
			student_label = result["student_id"] or "New learner"
			st.markdown(f"**Ranked courses for learner {student_label}**")
			st.dataframe(
				recommendations,
				hide_index=True,
				width="stretch",
				column_config={
					"Match Score": st.column_config.NumberColumn(format="percent"),
					"Why Recommended": st.column_config.TextColumn(width="large"),
				},
			)
		with result_right:
			render_figure(st, make_match_figure(recommendations))

		st.markdown("#### Your profile vs. similar students")
		similar = result["similar_learners"]
		st.caption(f"Compared with {len(similar)} nearest learners in the training data.")
		render_figure(st, make_profile_figure(result["profile"], similar))
	else:
		st.info("Submit a learner profile to see ranked course recommendations.")

st.markdown('<div id="recommended-resources" class="section-anchor"></div>', unsafe_allow_html=True)
with numbered_panel(st, 5, "Recommended Resources"):
	st.markdown(resource_data_notice())
	if result:
		st.markdown("**Recommended course codes**")
		for _, row in result["recommendations"].iterrows():
			st.markdown(f"`{row['Course']}` - {row['Match Score']:.1%} match")

st.caption(f"Dataset: {DATA_PATH.name} · Model: cosine similarity over learner profiles")

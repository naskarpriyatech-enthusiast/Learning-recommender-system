import json

import joblib

from src.config import METRICS_PATH, MODEL_DIR, MODEL_PATH
from src.data_loader import load_dataset
from src.recommender import train_recommender


def main() -> None:
	frame = load_dataset()
	bundle, metrics = train_recommender(frame)
	MODEL_DIR.mkdir(parents=True, exist_ok=True)
	joblib.dump(bundle, MODEL_PATH)
	METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

	print(f"Model saved to {MODEL_PATH}")
	print(f"Metrics saved to {METRICS_PATH}")
	print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
	main()

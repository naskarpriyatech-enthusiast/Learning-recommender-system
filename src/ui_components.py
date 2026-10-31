from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def load_css(st: object, css_path: Path) -> None:
	if css_path.exists():
		css = css_path.read_text(encoding="utf-8")
		st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


@contextmanager
def numbered_panel(st: object, number: int, title: str) -> Iterator[None]:
	with st.container(key=f"panel_{number}"):
		st.markdown(
			f'<div class="panel-header"><span class="badge">{number}</span>'
			f'<span class="panel-title">{title}</span></div>',
			unsafe_allow_html=True,
		)
		yield

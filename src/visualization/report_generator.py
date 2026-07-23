from pathlib import Path
from typing import Dict, List


HTML_TEMPLATE = """
<!doctype html>
<html>
	<head>
		<meta charset="utf-8">
		<title>{title}</title>
		<style>
			body {{ font-family: Arial, sans-serif; margin: 20px; }}
			h1 {{ color: #2c3e50; }}
			section {{ margin-bottom: 24px; }}
		</style>
	</head>
	<body>
		<h1>{title}</h1>
		{body}
	</body>
</html>
"""


def generate_html_report(title: str, sections: Dict[str, str], output_path: str) -> Path:
		"""Create a minimal HTML report with titled sections.

		sections: mapping from heading -> HTML or plain text body.
		"""
		body = []
		for heading, content in sections.items():
				body.append(f"<section><h2>{heading}</h2><div>{content}</div></section>")
		html = HTML_TEMPLATE.format(title=title, body="\n".join(body))
		p = Path(output_path)
		p.parent.mkdir(parents=True, exist_ok=True)
		p.write_text(html, encoding="utf-8")
		return p


__all__ = ["generate_html_report"]


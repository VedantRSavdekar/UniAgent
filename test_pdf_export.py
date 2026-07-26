from App.services.pdf_export_service import generate_report_pdf

fake_career_report = """
### 1. Profile Snapshot
| Name | Vedant |
| ---- | ------ |
Some text with <br> a line break and \u2011 non-breaking hyphen (should NOT be a black box) and *italics* and **bold**.
Self\u2011described AI Engineer with Retrieval\u2011Augmented Generation experience.
More content here to simulate a real report with – en-dash and — em-dash characters.
Curly quotes: “like this” and ‘this’ should convert to straight quotes.
"""

fake_job_results = """
Job listings
- Some Job at Some Company — [Apply here](https://example.com)
- Another Job at Another Company — [Apply here](https://example.com)
"""


class FakeATSResult:
    overall_score = 55
    format_score = 55
    keyword_match_score = None
    format_issues = [
        "Uses tables. Avoid HTML tags like <br>.",
        "Missing dates.",
    ]
    matched_keywords = []
    missing_keywords = []
    recommendations = [
        "Fix formatting.",
        "Add dates.",
    ]


if __name__ == "__main__":
    pdf_bytes = generate_report_pdf(
        career_report=fake_career_report,
        job_results=fake_job_results,
        ats_result=FakeATSResult(),
    )

    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes)

    print("Done — check test_output.pdf in this folder")
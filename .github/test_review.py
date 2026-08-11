#!/usr/bin/env python3
# python3 .github/test_review.py
from review import tag_lines, usable_comments

DIFF = """diff --git a/styles.css b/styles.css
--- a/styles.css
+++ b/styles.css
@@ -10,3 +10,4 @@ body {
 .hero {
-  color: red;
+  color: #123456;
+  margin: 0;
 }
"""

tagged, valid = tag_lines(DIFF)
assert valid["styles.css"] == {10, 11, 12, 13}, valid  # .hero 10, adds 11-12, brace 13
assert "styles.css:11: +  color: #123456;" in tagged, tagged
assert "-  color: red;" in tagged and "styles.css:-" not in tagged  # deletions stay bare

keep = usable_comments({"comments": [
    {"path": "styles.css", "line": 11, "body": "x"},
    {"path": "styles.css", "line": 999, "body": "not in the diff, should vanish"},
    {"path": "nope.css", "line": 11, "body": "file not in the diff either"},
    {"path": "styles.css", "line": 12, "start_line": 11, "body": "multiline"},
]}, valid)
assert len(keep) == 2, keep
assert keep[0] == {"path": "styles.css", "line": 11, "side": "RIGHT", "body": "x"}
assert keep[1]["start_line"] == 11 and keep[1]["start_side"] == "RIGHT", keep[1]
print("ok")

import re

from unittest import TestCase

class TestPatterns(TestCase):
    pass

causallinks = open("causal_links.txt", 'r', encoding="utf-8")
lines = causallinks.readlines()
i = 0
for txt in lines:
    if len(txt) == 0 or re.match(r"[\s]+$", txt):
            continue
    if re.match(r"#", txt):
        continue
    ptxt = re.search(r'(?<={)(.+)(?=})', txt).group(0)
    etxt = re.findall(r'(?<=\[)([^\]]+)(?=\])', txt)
    if not len(etxt):
        continue
    etxt = etxt[0]
    def ex(self):
        actual = "hi"
        assert actual == etxt, f"Expected {etxt}. Got {actual}"
    setattr(TestPatterns, f"test_{i}", ex)
    i += 1
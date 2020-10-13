import re

from unittest import TestCase

from pattern_match import find_match

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
        match = find_match(etxt)
        print(match)
        assert match, f"Couldn't find match for {etxt}"
    setattr(TestPatterns, f"test_{i}", ex)
    i += 1
import argparse
import os
import re
import operator
import csv
import codecs
from cmyPackage import *

from cmyPatternMatching import *

def Patterns_to_csv(outfile):
    csvfile = codecs.open(outfile, 'w', 'utf8')
    writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["pid", "freq", "is_one_sent", "table", "line", "col" ,"ptxt", "etxt", "maintoken"])

    causaltxt = ReadFile(os.path.join(corpdir, 'causal_links.txt'))
    causal_txt_lines = causaltxt.splitlines()
    Patterns = []
    ptid = 0
    for txt in causal_txt_lines:
        ### ---- if a line is a empty string, skip it ----
        if len(txt) == 0 or re.match(ur"[\s]+$", txt):
            continue
        ### ---- if a line started with '#', it is a comment line, skip it ----
        if re.match(ur"#", txt):
            continue
        ### ---- get the 3-level type for each pattern ----
        ptidx = [int(i) for i in list((re.match(ur'(\d+) (\d+) (\d+) (\d+) (\d+)', txt)).groups())]
        ### ---- get pattern text for each pattern ----
        ptxt = re.search(ur'(?<={)(.+)(?=})', txt).group(0)
        ### ---- get example text list for each pattern ---- 
        etxt = re.findall(ur'(?<=\[)([^\]]+)(?=\])', txt)
        ### ---- create a 'pattern' type object and append it into "Patterns" list ----
        pt = pattern(ptidx[0], ptidx[1], ptidx[2:], ptxt, etxt, ptid)
        print(pt.main_token)
        row = [ptid, ptidx[0], ptidx[1], ptidx[2], ptidx[3], ptidx[4], ptxt, etxt, pt.main_token]
        writer.writerow(row)
        ptid += 1
    #write new AS pattern
    writer.writerow([ptid,0,0,3,1,1,'as &C , &R', 'As the water flows into the body of water, it slows down and drops the sediment it was carrying.', "[[u'As']]"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to generate new patterns.csv")
    parser.add_argument("--outfile", type=str, help="path to patterns csv output file, corresponds to patterns_typology.csv in repo") #'patterns_typology.csv'
    args = parser.parse_args()
    if args.outfile:
        Patterns_to_csv(args.outfile)


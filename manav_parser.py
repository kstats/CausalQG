import argparse
import re
import csv

def parse(input_file, output_file):
    txt = ''
    with open(input_file, 'r', encoding='utf-8') as f:
        txt = ''.join(f.readlines())
    
    ptrn = re.compile("[.?!\s]?([a-zA-z][a-zA-z\s]+[.?!\s]?) ([cC]onsequently), ([a-zA-z\s]+[.?!])")
    matches = ptrn.findall(txt)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Cause", "Connector", "Effect"])
        writer.writerows([[matches[0], matches[1], matches[2]] for matches in matches])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--input', type=str, help='The path to the input file \
        or directory')
    parser.add_argument('--output', type=str, help='The path to the output file \
        or directory')
    
    args = parser.parse_args()
    
    parse(args.input, args.output)


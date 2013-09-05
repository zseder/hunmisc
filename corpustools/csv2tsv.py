"""This script converts csv to tsv, and that is not that simple as it seems,
because csv can have commas in double quotes

"""
import sys

def parse_csv(s):
    s = s.strip()
    start_dquote_index = s.find("\"")
    # look for double quote intervals
    while start_dquote_index >= 0:
        end_dquote_index = s.find("\"", start_dquote_index + 1)

        # replace commas inside double quotes
        s = (s[:start_dquote_index] +
             s[start_dquote_index:end_dquote_index+1].replace(",", "<comma>") +
             s[end_dquote_index+1:])
        new_end_dquote_index = s.find("\"", start_dquote_index + 1)
        start_dquote_index = s.find("\"", new_end_dquote_index + 1)

    # replace <comma> with real comma
    return [v.replace("<comma>", ",") for v in s.split(",")]

def to_tsv(l):
    return "\t".join(l)

def main():
    for l in sys.stdin:
        print to_tsv(parse_csv(l))

if __name__ == "__main__":
    main()

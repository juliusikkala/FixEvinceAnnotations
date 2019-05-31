#!/usr/bin/env python3
import sys
import re

def main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " inputfile outputfile")
        return

    input_file = open(sys.argv[1], "rb")
    data = input_file.read()
    input_file.close()
    output = open(sys.argv[2], "wb")

    # The Evince issue #1008 causes the y-coordinate of the clickable area of a
    # highlight to not match with the actual highlight location. Search for the
    # highlights in the PDF and copy the correct y-coordinates from the actual
    # highlight.
    highlight_pattern = re.compile(b'\/Type \/Annot \/Rect \[([^]]*)] \/Subtype \/Highlight \/QuadPoints \[([^]]*)]')

    last_pos = 0
    while True:
        match = highlight_pattern.search(data, last_pos)
        if match == None:
            break
        last_pos = match.end()
        clickable = match.group(1).split(b' ')
        highlight = match.group(2).split(b' ')
        if len(clickable) != 5 or len(highlight) != 9 or clickable[0] != highlight[0]:
            continue

        clickable[3] = highlight[1].split(b'.')[0]
        clickable[1] = highlight[5].split(b'.')[0]

        reconstructed = (
            b'/Type /Annot /Rect [' + b' '.join(clickable) +
            b'] /Subtype /Highlight /QuadPoints [' + b' '.join(highlight) + b']'
        )
        data = data[:match.start()] + reconstructed + data[match.end():]

    output.write(data)
    output.close()


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print(e.filename + ": " + e.strerror)

import re
from collections import defaultdict

# Path to your C++ file
cpp_file = "./include/colours.hpp"

# Regex to match lines like: static const CRGBW White = CRGBW(0, 0, 0, 255);
pattern = re.compile(r"static const CRGBW \w+\s*=\s*CRGBW\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([A-Za-z0-9_]+)\s*\)")

colors  = defaultdict(list)  # Map from (r,g,b,w) to list of variable names

nb_lines = 0
with open(cpp_file, "r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, 1):
        nb_lines += 1
        print(f"Processing line {nb_lines}: {line.strip()}")
        match = pattern.search(line)
        if match:
            r, g, b, w = match.groups()
            colors[(r, g, b, w)].append(line)
print(f"Processed {nb_lines} lines.")

# Print duplicates
print("Duplicate color values found:")
for color_vals, names in colors.items():
    if len(names) > 1:
        print(f"{color_vals}: {', '.join(names)}")

import os
import re

def parse_captions(path):
    """Parse lines from captions"""
    lines = []
    for fname in os.listdir(path):
        if re.findall(r'\.vtt$', fname):
            with open(os.path.join(path, fname), 'r') as f:
                get_next = False
                for line in f.readlines():
                    if re.match(r'\d\d:\d\d:\d\d\.\d\d\d --> \d\d:\d\d:\d\d\.\d\d\d', line):
                        get_next = True
                    elif get_next:
                        lines.append(line[:-1])
                        get_next = False
                        
    return "\n".join(lines)

"""Contains patterns that ICHOR looks for in output files from Gaussian/AIMALL."""

import re

COORDINATE_LINE = re.compile(r"\s*\w+(\s*[+-]?\d+.\d+\s*){3}$")
AIMALL_LINE = re.compile(r"[<|]?\w+[|>]?\s+=(\s+[+-]?\d+.\d+([Ee]?[+-]?\d+)?)")
MULTIPOLE_LINE = re.compile(r"Q\[\d+,\d+(,\w+)?]\s+=\s+[+-]?\d+.\d+([Ee]?[+-]?\d+)?")
SCIENTIFIC = re.compile(r"[+-]?\d+.\d+([Ee]?[+-]?\d+)?")

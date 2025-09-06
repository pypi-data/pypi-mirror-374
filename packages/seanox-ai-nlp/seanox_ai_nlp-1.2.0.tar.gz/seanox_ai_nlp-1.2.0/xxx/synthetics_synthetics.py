# tests/test_synthetics_synthetics.py

from seanox_ai_nlp.synthetics import synthetics
from time import perf_counter
from pathlib import Path

import pathlib
import random
import copy
import json
import pytest

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")
EXAMPLES_PATH = Path("./examples") if Path("./examples").is_dir() else Path("../examples")



with open(TESTS_PATH / "synthetics-planets_de.json", encoding="utf-8") as file:
    datas = json.load(file)

count_text = 0
start = perf_counter()
for data in datas:
    result = synthetics(TESTS_PATH, "synthetics_de_annotate.yaml", data)
    count_text += len(result.text)
end = perf_counter()


import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True, slots=True)
class ParsedLine:
    raw: str


@dataclass(frozen=True, slots=True)
class Dependency(ParsedLine):
    TYPE = "dependency"
    RE_INCLUDE = re.compile(r"^\s*include\s+(git=.+)\s*$")
    spec: str


@dataclass(frozen=True, slots=True)
class RawLine(ParsedLine):
    TYPE = "raw"


def _parse_line(line: str) -> ParsedLine:
    if m := Dependency.RE_INCLUDE.match(line):
        return Dependency(line, m.group(1))
    return RawLine(line)


def parse(src: Path) -> Iterator[ParsedLine]:
    with open(src, "r") as f:
        for line in f:
            yield _parse_line(line)

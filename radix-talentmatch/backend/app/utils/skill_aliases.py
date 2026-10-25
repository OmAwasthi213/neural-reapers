"""Small explicit aliases for genuinely equivalent skill names."""
import re


def normalize(name: str) -> str:
    return "".join(ch.lower() for ch in name if ch.isalnum())


ALIASES = {
    "dsa": "Data Structures and Algorithms",
    "datastructuresandalgorithms": "Data Structures and Algorithms",
    "oop": "Object-Oriented Programming",
    "objectorientedprogramming": "Object-Oriented Programming",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ml": "Machine Learning",
    "machinelearning": "Machine Learning",
}


def canonical_name(name: str) -> str:
    clean = name.strip()
    return ALIASES.get(normalize(clean), clean)


def canonical_key(name: str) -> str:
    return normalize(canonical_name(name))

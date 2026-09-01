"""Every module under src/ has to import.

Three of them did not. They were left behind when the mass-application engine
was removed, they referenced a module that no longer exists, and nothing caught
it because nothing imported them either. One of those dead files was the only
thing pulling in langchain-huggingface, and through it torch, transformers and
scikit-learn: 902 MB of an install nobody could reach.

A module that cannot be imported is either broken or dead. Both are worth
failing the build over.
"""

import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"


def modules():
    """Walk the files, not the packages.

    pkgutil.walk_packages has to import a package before it can descend into it,
    and src/libs has no __init__.py, so it found 5 of the 27 files and quietly
    reported success on the rest.
    """
    found = []
    for path in sorted(SRC.rglob("*.py")):
        parts = path.relative_to(ROOT).with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        found.append(".".join(parts))
    return found


@pytest.mark.parametrize("name", modules())
def test_module_imports(name):
    importlib.import_module(name)


def test_the_walk_reaches_the_nested_packages():
    """Without this the parametrisation could silently shrink to a handful of
    modules and every assertion above would pass by not looking."""
    names = modules()
    assert len(names) >= 20, f"only {len(names)} modules found, the walk is broken"
    assert any("resume_and_cover_builder" in n for n in names)

#!/usr/bin/env python3
"""Run the RDF regression test suite and emit JUnit XML reports."""

from pathlib import Path
import sys

try:
    import xmlrunner
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        'Missing dependency: unittest-xml-reporting (xmlrunner).\n'
        'Install with: python3 -m pip install --user unittest-xml-reporting\n'
    )
    raise SystemExit(1) from exc

import unittest

def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    reports_dir = repo_root / 'rdf.test' / 'logs'
    reports_dir.mkdir(parents=True, exist_ok=True)

    suite = unittest.defaultTestLoader.discover('tests')
    runner = xmlrunner.XMLTestRunner(output=str(reports_dir), outsuffix='')
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main())

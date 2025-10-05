import difflib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path
import unittest


class RobustDesignFlowCLITests(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree('rdf.test', ignore_errors=True)

    def test_cli_run_generates_expected_report(self):
        repo_root = Path(__file__).resolve().parents[1]
        config_path = repo_root / 'scripts' / 'sample_run.yml'
        self.assertTrue(config_path.is_file())

        env = os.environ.copy()

        cmd = [
            sys.executable,
            'scripts/robust_design_flow.py',
            '-t',
            '-r',
            '-v',
            '-y',
            '-c',
            str(config_path.relative_to(repo_root)),
            '-d',
            'gcd',
            '-n',
            'nangate45',
        ]

        proc = subprocess.Popen(
            cmd,
            cwd=repo_root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        def _drain(stream, collector, dest):
            for line in iter(stream.readline, ''):
                collector.append(line)
                dest.write(line)
                dest.flush()
            stream.close()

        threads = [
            threading.Thread(target=_drain, args=(proc.stdout, stdout_lines, sys.stdout), daemon=True),
            threading.Thread(target=_drain, args=(proc.stderr, stderr_lines, sys.stderr), daemon=True),
        ]

        for thread in threads:
            thread.start()

        return_code = proc.wait()
        for thread in threads:
            thread.join()

        if return_code != 0:
            stdout_text = ''.join(stdout_lines)
            stderr_text = ''.join(stderr_lines)
            self.fail(
                "RDF flow failed:\n"
                f"STDOUT:\n{stdout_text}\n"
                f"STDERR:\n{stderr_text}"
            )

        work_home = repo_root / 'rdf.test'
        report_path = work_home / 'logs' / 'nangate45' / 'gcd' / 'base' / '6_report.log'
        self.assertTrue(report_path.is_file(), 'Missing stage 6 report log')

        golden_report = repo_root / 'tests' / 'golden' / '6_report.log.ok'
        produced = self._normalize_report(report_path.read_text())
        expected = self._normalize_report(golden_report.read_text())
        if produced != expected:
            diff = '\n'.join(
                difflib.unified_diff(
                    expected.splitlines(),
                    produced.splitlines(),
                    fromfile='expected',
                    tofile='produced',
                    lineterm='',
                )
            )
            self.fail(f"Normalized report mismatch:\n{diff}")

        json_report_path = work_home / 'logs' / 'nangate45' / 'gcd' / 'base' / '6_report.json'
        self.assertTrue(json_report_path.is_file(), 'Missing stage 6 report JSON')

        golden_json_path = repo_root / 'tests' / 'golden' / '6_report.json.ok'
        produced_json = json.loads(json_report_path.read_text())
        expected_json = json.loads(golden_json_path.read_text())

        self.assertEqual(
            set(produced_json.keys()),
            set(expected_json.keys()),
            'JSON keys differ between produced and golden reports',
        )

        for key, expected_value in expected_json.items():
            produced_value = produced_json[key]
            if isinstance(expected_value, float):
                self.assertTrue(
                    math.isclose(produced_value, expected_value, rel_tol=1e-6, abs_tol=1e-9),
                    f"Mismatch for {key}: expected {expected_value}, got {produced_value}",
                )
            else:
                self.assertEqual(
                    produced_value,
                    expected_value,
                    f"Mismatch for {key}: expected {expected_value}, got {produced_value}",
                )

    @staticmethod
    @staticmethod
    def _normalize_report(text: str) -> str:
        normalized = text
        normalized = re.sub(r'/[^\s]*/Robust-Design-Flow', '<REPO>', normalized)
        normalized = normalized.replace('/workspace', '<REPO>')

        filtered = []
        for line in normalized.splitlines():
            if 'Log                        Elapsed/s Peak Memory/MB' in line:
                break
            if 'Elapsed time:' in line or 'CPU time:' in line or 'Peak memory:' in line:
                continue
            filtered.append(line.rstrip())
        return '\n'.join(filtered).strip()


if __name__ == '__main__':
    unittest.main()

# RDF Test Harness

This folder contains an end-to-end regression for the Robust Design Flow (RDF).
The test runs the full OpenROAD flow on the `gcd` design for the Nangate45
platform and compares the resulting report artifacts against the goldens in
`tests/golden/`.

## Prerequisites

- OpenROAD-flow-scripts and its toolchain must be built (see the repository
  `README.md` for build instructions).
- `make`, `python3`, and all runtime dependencies required by ORFS must be on
  your `PATH`.

## Running the Regression

From the repository root:

```bash
python3 -m unittest discover -s tests
```

This takes about a minute and streams the full flow output to the terminal so
you can watch each stage execute. Temporary results live in `rdf.test/` while
 the test runs and are cleaned up automatically afterward.

## Updating Golden Artifacts

If the flow metrics legitimately change (e.g., due to tool updates):

1. Run the flow manually to generate fresh artifacts:
   ```bash
   python3 scripts/robust_design_flow.py -t -r -y -v \
     -c scripts/sample_run.yml -d gcd -n nangate45
   ```
2. Copy the new report files into the golden directory:
   ```bash
   cp rdf.test/logs/nangate45/gcd/base/6_report.log tests/golden/6_report.log.ok
   cp rdf.test/logs/nangate45/gcd/base/6_report.json tests/golden/6_report.json.ok
   ```
3. Remove `rdf.test/` when done: `rm -rf rdf.test`.
4. Re-run the regression to confirm parity.

## Troubleshooting

- If the test fails because `make` or OpenROAD is not found, verify that the
  ORFS environment setup scripts have been sourced.
- To inspect a failing run, comment out the `tearDown` cleanup in
  `tests/test_robust_design_flow.py` so the `rdf.test/` directory is preserved
  for manual inspection.

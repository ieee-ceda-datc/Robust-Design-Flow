# RDF Test Harness

This directory exercises the Robust Design Flow (RDF) end-to-end on the `gcd`
design (Nangate45) and compares the reported metrics against the goldens in
`tests/golden/`.

## Recommended: Run in Docker

Build the container image (from the repository root):

```bash
docker build -t rdf-openroad-ci -f docker/Dockerfile .
```

Run the regression inside the image, mounting your working copy at
`/workspace`:

```bash
docker run --rm -it \
  -v "$PWD":/workspace \
  rdf-openroad-ci \
  bash -lc "python3 tests/run_regression.py"
```

This matches the Jenkins CI environment and prints the full flow log.

## Updating Golden Artifacts

When tool updates legitimately change the reported metrics:

1. Regenerate the reports in Docker:
   ```bash
   docker run --rm -it \
     -v "$PWD":/workspace \
     rdf-openroad-ci \
     bash -lc "python3 scripts/robust_design_flow.py -t -r -y -v \\
       -c scripts/sample_run.yml -d gcd -n nangate45"
   ```
2. Copy the updated files back onto the host:
   ```bash
   cp rdf.test/logs/nangate45/gcd/base/6_report.log tests/golden/6_report.log.ok
   cp rdf.test/logs/nangate45/gcd/base/6_report.json tests/golden/6_report.json.ok
   ```
3. Clean up the temporary workspace:
   ```bash
   rm -rf rdf.test
   ```
4. Re-run `python3 tests/run_regression.py` (or the Docker command above) to
   confirm parity.

## Tips

- The test fixture removes `rdf.test/` after each run. Comment out
  `tearDown()` in `tests/test_robust_design_flow.py` if you need to inspect the
  intermediate flow outputs while debugging.
- To use a prebuilt installation located elsewhere (for example
  `/opt/Robust-Design-Flow` on Jenkins), set `RDF_INSTALL_ROOT` before running
  the regression. When unset, the scripts default to the current working copy.
- If you choose to run natively (outside Docker), ensure OpenROAD-flow-scripts
  is built, the toolchain is on `PATH`, and Python has `unittest-xml-reporting`
  and `PyYAML` installed.

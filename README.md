DATC Robust Design Flow
===
The [Design Automation Technical Committee (DATC)](https://ieee-ceda.org/activities/technical-committees/datc),  is a technical member committee of IEEE [Council on Electronic Design Automation (CEDA)](https://ieee-ceda.org/).  The mission of DATC is to serve as a central organization and platform
that addresses key challenges in design automation, facilitates collaboration on public design flows and testcases, and organizes relevant workshops, meetings, and publications. 
In recent years, DATC efforts have focused on building public design flows, defining key metrics, and enabling ML EDA. The overarching goal is to ensure continuous progress in EDA research by maintaining baseline calibrations, 
tracking metrics, and integrating point CAD tools into a cohesive flow to promote cross-stage research and innovation.

A critical part of DATC activities every year includes maintaining and enhancing a public flow available in this repository called the Robust Design Flow (RDF). IEEE DATC RDF is intended (i) to preserve and integrate leading research codes, including those from past academic contests, and (ii) to provide a foundation and backplane for academic research in the RTL-to-GDS IC implementation arena. Unlike other open-source design flows RDF creates a framework to mix and match point tools at different stages of the flow. 



## DATC RDF: Getting Started

### Flow Configuration

We currently support an academic point tool-based configurable flow that is wrapped around the [Single-app integrated OpenROAD flow](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts).

#### Build RDF
RDF depends on [OpenROAD-flow-scripts](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts). Please refer build instructions from ORFS repository and [documentation](https://openroad-flow-scripts.readthedocs.io/en/latest/index2.html). Once ORFS is built, follow the instructions below to run RDF.

#### Containerised Setup (Recommended)

Build the provided Docker image from the repository root:

```bash
docker build -t rdf-openroad-ci -f docker/Dockerfile .
```

Run the regression inside the container (the current repository is mounted at
`/workspace`):

```bash
docker run --rm -it \
  -v "$PWD":/workspace \
  rdf-openroad-ci \
  bash -lc "python3 tests/run_regression.py"
```

The same image can be used by Jenkins (see `Jenkinsfile`) to keep the CI tool
chain reproducible. When running against a prebuilt installation (e.g.
`/opt/Robust-Design-Flow`), set `RDF_INSTALL_ROOT` to that path; otherwise the
scripts default to the current working copy.

#### Academic Point Tool-Based Configurable Flow

The academic point-tool-based flow is a conventional RDF flow that uses a flow configuration file in YAML format. An example RDF flow configuration file is shown below ([Example](./scripts/sample_run.yml)).


```yaml
synth:
  tool: openroad
  user_parms: []
floorplan:
  tool: openroad
  user_parms: []

global_place:
  tool: openroad
  user_parms: []

detail_place:
  tool: openroad
  user_parms: []

cts:
  tool: openroad
  user_parms: []

global_route:
  tool: openroad
  user_parms: []

detail_route:
  tool: openroad
  user_parms: []

finish:
  tool: openroad
  user_parms: []
```

In the flow configuration, the user can set whether the flow points to the default OpenROAD implementation or a custom point tool.

#### Running the tool

An example run using the GCD design in OpenROAD for Nangate45 is shown below:

You can run the tool from the command line with the following script.

```shell
mkdir run
cd run
python3 ../scripts/robust_design_flow.py -r -c ../scripts/sample_run.yml -d gcd -n nangate45
```

When running in automation, add `-y` (or `--yes`) to skip the interactive confirmation prompts for each stage:

```shell
python3 ../scripts/robust_design_flow.py -r -y -c ../scripts/sample_run.yml -d gcd -n nangate45
```

Below we explain the different parameters available for our script. 

```
usage: RobustDesignFlow [-h] [-v | -q] [-t] [-y] -c CONFIG [-l LOG] (-r | -p) [-j JOB_ID] -d DESIGN [-m CUSTOM_DESIGN_MAKE] -n PLATFORM

Robust Design Flow (RDF).

options:
  -h, --help            show this help message and exit
  -v, --verbose         Enables verbose mode with detailed information.
  -q, --quiet           Suppresses all informational messages and only displays warnings and errors.
  -t, --test            Enables test mode override of the defaults
  -y, --yes             Automatically confirm each stage without prompting
  -c CONFIG, --config CONFIG
                        YAML file containing the target flow
  -l LOG, --log_file LOG
                        Log file for the run.
  -r, --run             Start a new run
  -p, --proceed         Continues an existing job or run.
  -j JOB_ID, --job_id JOB_ID
                        Enter the job_id of the run
  -d DESIGN, --design DESIGN
                        Name of the design in ORFS to run
  -m CUSTOM_DESIGN_MAKE, --custom_design_make CUSTOM_DESIGN_MAKE
                        Point to a custom design make file instead of an existing ORFS design
  -n PLATFORM, --platform PLATFORM
                        Define the ORFS platform for the selected design
```


Adding Your Pont Tool Binaries into RDF Flow
---

You can add your own point tool in the RDF configurable flow. First, put your point tool binary and necessary side files in the following directory:

```bash
./tools/<stage>/<tool_name>
```

where `<stage>` is the target design stage, e.g., global placement or detailed routing, and `<tool_name>` is the name of your tool. 

Next, you can add your tool in the flow configuration file, and the RDF Python script will call the custom make command to launch your tool.

An example make command is shown below.

```make
RDF_TRITON_ROUTE_EXE =  $(RDF_ROOT_DIR)/../tools/detail_route/TritonRoute/TritonRoute

rdf_run_TritonRoute:
	$(RDF_TRITON_ROUTE_EXE) -lef $(TECH_LEF) -def $(RDF_DEF_FILE) -guide $(RESULTS_DIR)/route.guide -output $(RDF_DEF_OUT)
```

Users in the makefile will have access to all the variables that are provided by OpenROAD, such as `TECH_LEF`, `SC_LEF`, `ADDITIONAL_LEFS`, and `SDC_FILE`. Users must add their tool to the makefile with the prefix rdf_run_<tool name in config yml>.

Additionally, the Python script will provide pointers to the source and destination DEF files or Verilog files for the tool to consume and generate, i.e., `RDF_DEF_FILE`, `RDF_VERILOG_FILE`, and `RDF_DEF_OUT`. Any additional user parameters passed to the YAML file will be passed as Makefile variables with the RDF prefix. 


Contributing Your Tool to DATC RDF
---

We welcome contributions to DATC RDF. Contributions include:
- Source code of your point tool that can be added as a submodule to our tools directory with the updated Makefile containing the new make target and yaml to support the new tool.
If your point tool is distributable, you can also add the binary to our tools directory, along with details in the README on the system configuration in which that binary was built. This should also be accompanied by an update to the Makefile with a new target and the corresponding YAML file. 
- New testcases and enablements


To contribute, create a PR to this GitHub repository. Developer certificates will be provided for significant contributions at next year's ICCAD Contest Special Session. 

References
---
1. V. A. Chhabria, V. Gopalakrishnan, A. B. Kahng, S. Kundu, Z. Wang, B.-Y. Wu and D. Yoon, "Strengthening the Foundations of IC Physical Design and ML EDA Research", 
*Proc. International Conference on Computer-Aided Design*, 2024.

2. A. B. Kahng and Z. Wang, "DG-RePlAce: A Dataflow-Driven GPU-Accelerated Analytical Global Placement Framework for Machine Learning Accelerators", 
*IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*, 2024.

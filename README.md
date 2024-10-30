DATC Robust Design Flow
===

IEEE DATC Robust Design Flow (DATC RDF) is intended (i) to preserve and integrate leading research codes, including from past academic contests, and (ii) to  provide a foundation and backplane for academic research in the RTL-to-GDS IC implementation arena.

DATC RDF: Getting Started
---

### Flow Configuration

We currently support the an Academic point tool-based configurable flow that is wrapped around the [Single-app integrated OpenROAD flow.](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts).


#### Academic Point Tool-Based Configurable Flow

The academic point-tool based flow is a conventional RDF flow, which uses a flow configuration file in YAML format.
An example RDF flow configuration file is shown below ([Example](./scripts/sample_run.yml)).

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

In the flow configuration, the user can set wether the flow points to the default OpenROAD implemenation or a custom point tool.

#### Running the tool

You can run the toll from the command line with the following script. 

```shell
python3 <scripts_dir>/robust_design_flow.py
```

```
usage: RobustDesignFlow [-h] [-v | -q] [-t] -c CONFIG [-l LOG] (-r | -p) [-j JOB_ID] -d DESIGN [-m CUSTOM_DESIGN_MAKE] -n PLATFORM

Robust Design Flow(RDF).

options:
  -h, --help            show this help message and exit
  -v, --verbose         Enables verbose mode with detailed information.
  -q, --quiet           Supresses all informational messages and only displays warnings and errors.
  -t, --test            Enables test mode override of the defaults
  -c CONFIG, --config CONFIG
                        YAML file containing the target flow
  -l LOG, --log_file LOG
                        Log file for run.
  -r, --run             Start a new run
  -p, --proceed         Continues an existing job or run.
  -j JOB_ID, --job_id JOB_ID
                        Enter the job_id of the run
  -d DESIGN, --design DESIGN
                        Name of the design in ORFS to run
  -m CUSTOM_DESIGN_MAKE, --custom_design_make CUSTOM_DESIGN_MAKE
                        Point to a custom design make file instead of an exisitng ORFS design
  -n PLATFORM, --platform PLATFORM
                        Define the ORFS platform for the selected design
```

An example run using the GCD design in OpenROAD for Nangate45 is below:

```shell
python3 ../scripts/robust_design_flow.py -r -c ../scripts/sample_run.yml -d gcd -n nangate45
```


Adding Your Pont Tool Binaries into RDF Flow
---

You can add your own point tool in the RDF configurable flow.
First, put your point tool binary and necessary side files in the directory:

```bash
./tools/<stage>/<tool_name>
```

where `<stage>` is the target design stage, e.g., global placement or detailed routing, and `<tool_name>` is the name of your own tool.
Then, create the Python runner script, named:

```bash
./bin/<stage>/<tool_name>/rdf_<tool_name>.py
```

Then, you can add your tool in the flow configuration file, and RDF pyhton script will call the custom make command to launch your tool.

An example make command is shown below.

```make
RDF_TRITON_ROUTE_EXE =  $(RDF_ROOT_DIR)/../tools/detail_route/TritonRoute/TritonRoute

rdf_run_TritonRoute:
	$(RDF_TRITON_ROUTE_EXE) -lef $(TECH_LEF) -def $(RDF_DEF_FILE) -guide $(RESULTS_DIR)/route.guide -output $(RDF_DEF_OUT)
```

User in the makefile will have access to all the variables that are provided by OpenROAD such as `TECH_LEF, SC_LEF ADDITIONAL_LEFS, SDC_FILE`. Users must add their tool to the makfeile with the prefix `rdf_run_<tool name in config yml>`

Additionaly the python script will provide pointer to the source and destination DEF files or verilog files for the tool to consume and generate, i.e. `RDF_DEF_FILE`, `RDF_VERILOG_FILE` and `RDF_DEF_OUT`. Any additional user paramters passed to the yml file will be passed as Makefile variables with the RDF prefix. 


Contributing Your Tool into DATC RDF
---

We welcome contributions to DATC RDF.

References
---
1.

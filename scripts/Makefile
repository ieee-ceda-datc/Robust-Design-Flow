RDF_ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
ORFS_MAKE = $(RDF_ROOT_DIR)/../tools/OpenROAD-flow-scripts/flow/Makefile
FLOW_HOME = $(RDF_ROOT_DIR)/../tools/OpenROAD-flow-scripts/flow

include $(ORFS_MAKE)

compile_odb:
	ODB_FILE=$(RDF_ODB_FILE) DEF_FILE=$(RDF_DEF_FILE) $(OPENROAD_CMD) $(RUN_SCRIPT)

.PHONY: create_def
create_verilog:
	ODB_FILE=$(RDF_ODB_FILE) VERILOG_FILE=$(RDF_VERILOG_FILE) $(OPENROAD_CMD) $(SCRIPTS_DIR)/write_verilog.tcl

.PHONY: create_def
create_def:
	ODB_FILE=$(RDF_ODB_FILE) DEF_FILE=$(RDF_DEF_FILE) $(OPENROAD_CMD) $(SCRIPTS_DIR)/write_def.tcl

#Supported valiables accesible in the makefile
# TECH_LEF
# SC_LEF
# ADDITIONAL_LEFS
# DEF_FILE
# SDC_FILE
# ###
# CUSTOM OUTPUTS BY THE TOOL:
# ###
# RDF_DEF_FILE: def from previous stage
# RDF_VERILOG_FILE: verilog from previous stage
# RDF_<USER_PARAMS>: user params provided in the yml will be tranlated to variable passed to the makefile.
# example:   ROUTE: route.guide 
#            RDF_ROUTE=route.guide
# ###
# Expected files to be set
# ###
# RDF_DEF_OUT: location of def of the output
##############################
# Example tool Triton toute
##############################
RDF_TRITON_ROUTE_EXE =  $(RDF_ROOT_DIR)/../tools/detail_route/TritonRoute/TritonRoute

rdf_run_TritonRoute:
	$(RDF_TRITON_ROUTE_EXE) -lef $(TECH_LEF) -def $(RDF_DEF_FILE) -guide $(RESULTS_DIR)/route.guide -output $(RDF_DEF_OUT)
	@ehco $(RDF_TEST)
	@echo $(RDF_ROUTE) 
	

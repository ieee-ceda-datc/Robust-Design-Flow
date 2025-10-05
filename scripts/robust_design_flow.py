##########################################################################





# Original file copied and modified from RDF2020
# File name      : rdf.py
# Author         : Jinwook Jung (jinwookjung@ibm.com)
##########################################################################

import argparse
import shutil
import yaml
import logging
import os
import subprocess
from pathlib import Path
from datetime import datetime


class RobustDesignFlow():
    def __init__(self):
        self.auto_confirm = False
        # self.config = None
        # self.flow = None
        # self.design_dir = None
        # self.design_config = None
        # self.lib_dir = None
        # self.lib_config = None
    
    def create_logger(self, log_file=None,severity=None):
        # Create a custom logger
        logging.addLevelName(25,'STATUS')
        logger = logging.getLogger('RDF')
        # Create handlers
        c_handler = logging.StreamHandler()
        if severity is None:
            logger.setLevel('STATUS')
            c_handler.setLevel('STATUS')
        else:
            logger.setLevel(severity)
            c_handler.setLevel(severity)
        # Create formatters and add it to handlers
        c_format = logging.Formatter('[%(name)s][%(levelname)s] %(message)s')
        c_handler.setFormatter(c_format)
        
        # Add handlers to the logger
        logger.addHandler(c_handler)
        # handle log file
        if log_file is not None:
            f_handler = logging.FileHandler(str(log_file.absolute()))
            if severity is None:
                f_handler.setLevel('INFO')
            else:
                f_handler.setLevel(severity)
            f_format = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s][%(message)s]')
            f_handler.setFormatter(f_format)
            logger.addHandler(f_handler)
        return logger

    def process_config(self, config_yml):
        self.logger.info("Processing config file...")

        with open(config_yml) as f:
            self.config = yaml.safe_load(f)

        # FIXME: Get the RDF installation directory from user config file.
        self.valid_stages = {
            "synth":{"cur_stage": "synth" , "prev_stage": None},
            "floorplan": {"cur_stage": f"{self.orfs_results}/2_2_floorplan_macro.odb" , "prev_stage": f"{self.orfs_results}/2_1_floorplan.odb"},
            "global_place":{"cur_stage": f"{self.orfs_results}/3_3_place_gp.odb" , "prev_stage": f"{self.orfs_results}/3_2_place_iop.odb"},
            "detail_place": {"cur_stage": f"{self.orfs_results}/3_5_place_dp.odb" , "prev_stage": f"{self.orfs_results}/3_4_place_resized.odb"},
            "cts":{"cur_stage": f"{self.orfs_results}/4_1_cts.odb" , "prev_stage": f"{self.orfs_results}/3_place.odb"},
            "global_route":{"cur_stage": f"{self.orfs_results}/5_1_grt.odb" , "prev_stage": f"{self.orfs_results}/4_cts.odb"},
            "detail_route":{"cur_stage": f"{self.orfs_results}/5_2_route.odb" , "prev_stage": f"{self.orfs_results}/5_1_grt.odb"},
            "finish":{"cur_stage": "finish" , "prev_stage": f"{self.orfs_results}/5_route.odb"}
        }
        if not all(k in self.valid_stages.keys() for k in self.config.keys()):
            self.logger.error(f"Input YML file must contain options for all stages of the flow: {self.valid_stages}")
        
        self.flow = []
        for k, v in self.config.items():
            if v["tool"] == "openroad":
                run_cmds = self.orfs_stage(k)
                self.flow.extend(run_cmds)
            else:
                # TODO support for external tools
                run_cmds = self.non_orfs_stage(k, v)
                self.flow.extend(run_cmds)
                # raise NotImplementedError 

    def orfs_stage(self, yml_stage):
        stage = self.valid_stages[yml_stage]["cur_stage"]
        base_cmd = ""
        base_cmd += f"make -f {self.rdf_make} "
        base_cmd += f"DESIGN_CONFIG={self.orfs_design_mk} "
        base_cmd += f"WORK_HOME={self.workdir} "
        run_cmds = [base_cmd + stage]        
        return run_cmds

    def non_orfs_stage(self, yml_stage, params):
        prev_stage = self.valid_stages[yml_stage]["prev_stage"]
        stage = self.valid_stages[yml_stage]["cur_stage"]
        base_cmd = ""
        base_cmd += f"make -f {self.rdf_make} "
        base_cmd += f"DESIGN_CONFIG={self.orfs_design_mk} "
        base_cmd += f"WORK_HOME={self.workdir} "
        run_cmds = []
        #Ensure to run till prev stage
        custom_tool_cmd = base_cmd+ f"rdf_run_{params['tool']} "
        if prev_stage is not None:
            run_cmds += [base_cmd + prev_stage]
            run_cmds += self.create_def_verilog(prev_stage, base_cmd)
            custom_tool_cmd += f" RDF_DEF_FILE={prev_stage}.def "
        
        custom_tool_cmd += f" RDF_VERILOG_FILE={prev_stage}.v "
        custom_tool_cmd += f" RDF_DEF_OUT={stage}.def "


        for parameter, value in params["user_parms"].items():
            custom_tool_cmd += f" RDF_{parameter}={value} "

        run_cmds += [custom_tool_cmd]
        run_cmds += self.create_odb(stage, base_cmd)

        #TODO run the actual code.
        # For now I'm running ORFS
        run_cmds += self.orfs_stage(yml_stage)
        # run_cmds += self.create_def_verilog(stage, base_cmd)
        # run_cmds += [f"rm {stage}"]
        return run_cmds

    def create_def_verilog(self, stage, base_cmd):
        run_cmds = []
        write_verilog_cmd = base_cmd + " create_verilog " + \
                            f" RDF_ODB_FILE={stage} " +\
                            f" RDF_VERILOG_FILE={stage}.v" 
                            
        write_def_cmd = base_cmd + " create_def " +\
                            f" RDF_ODB_FILE={stage} " +\
                            f" RDF_DEF_FILE={stage}.def "
        run_cmds += [write_verilog_cmd]
        run_cmds += [write_def_cmd]
        return run_cmds

    def create_odb(self, stage, base_cmd):
        create_odb_cmd = base_cmd + " compile_odb " + \
                            f" RUN_SCRIPT={self.src_dir/'create_odb.tcl'} " +\
                            f" RDF_ODB_FILE={stage} " +\
                            f" RDF_DEF_FILE={stage}.def "
        return [create_odb_cmd]

    def run(self):
        for cmd in self.flow:
            self.logger.info(f"running cmd={cmd}")
            if not self.auto_confirm:
                _ = input("Confirm continue")
            p = subprocess.run(cmd,shell=True)
                
             
    def process_inputs(self):
        # Defaults
        script_dir = Path(__file__).resolve().parent.parent
        current_path = Path.cwd()
        
        parser = argparse.ArgumentParser(prog = "RobustDesignFlow",
                description = '''Robust Design Flow (RDF).''')
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-v", "--verbose", action="store_true",
                help = "Enables verbose mode with detailed information.")
        group.add_argument("-q", "--quiet", action="store_true",
                help = '''Suppresses all informational messages and only
                            displays warnings and errors.''')
        parser.set_defaults(func=lambda : parser.print_help())
        parser.add_argument("-t", "--test", action="store_true",
                help = "Enables test mode override of the defaults")
        parser.add_argument("-y", "--yes", action="store_true",
                help = "Automatically confirm each stage without prompting")
        
        parser.add_argument("-c",'--config', type=Path,
                                dest='config', required=True,
                                help = ''' YAML file containing the target flow''')
        
        parser.add_argument("-l", "--log_file", type=Path,
                help = "Log file for the run.",dest='log')
        
        # Mutually exclusive group to start a new run or contiunue an existing run.
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-r", "--run", action="store_true",
                help = "Start a new run")
        group.add_argument("-p", "--proceed", action="store_true",
                help = '''Continues an existing job or run.''')
        parser.add_argument("-j", "--job_id", type=Path,
                help="Enter the job_id of the run")
        
        
        parser.add_argument("-d", "--design", default="gcd", required=True,
                help = "Name of the design in ORFS to run")
        parser.add_argument("-m", "--custom_design_make",
                help = '''Point to a custom design make file instead of an existing ORFS design''')
        parser.add_argument("-n", "--platform", default="nangate45", required=True,
                help="Define the ORFS platform for the selected design")
        args = parser.parse_args()

        if ((not args.test) and args.proceed and (args.job_id is None)):
            parser.error("--proceed requires --job_id be set to continue an existing job.")

        if args.test:
            job_id = Path("rdf.test")
            if not args.proceed:
                shutil.rmtree(job_id, ignore_errors=True)
        elif args.job_id is None:
            job_id = Path(f"rdf.{datetime.now().strftime('%y%m%d.%H%M%S')}")
        else:
            job_id = args.job_id
        job_id.mkdir()
        self.workdir  = job_id
    
        self.src_dir = Path(__file__).resolve().parent
        self.orfs_dir = self.src_dir/"../tools/OpenROAD-flow-scripts"
        self.orfs_flow = self.orfs_dir/"flow"
        self.rdf_make = self.src_dir/"Makefile"
        # self.orfs_make = self.orfs_flow/"Makefile"
        self.orfs_platform = args.platform 
        self.orfs_design = args.design
        self.orfs_design_dir = self.orfs_flow/f"designs/{self.orfs_platform}/{self.orfs_design}"
        self.orfs_design_mk = self.orfs_design_dir/"config.mk"
        self.orfs_results = self.workdir/f"results/{self.orfs_platform}/{self.orfs_design}/base"
        
        if ((args.custom_design_make is not None) and args.design):
            if(args.platform is None):
                parser.error("--proceed requires --job_id be set to continue an existing job.")
            elif (not self.orfs_design_dir.is_dir()):
                parser.error(f"Using the default ORFS flow, cannot find design directory {self.orfs_design_dir}.")

        if args.verbose:
            severity = 'INFO'
        elif args.quiet:
            severity = 'WARNING'
        else:
            severity = None
        self.logger = self.create_logger( log_file = args.log,
                                        severity = severity)

        self.auto_confirm = args.yes

        rdf.process_config(args.config)
        self.logger.info(f"Running Job ID: {job_id}")

if __name__ == '__main__':
    rdf = RobustDesignFlow()
    rdf.process_inputs()
    #TODO support for continuing an existing run.
    rdf.run()

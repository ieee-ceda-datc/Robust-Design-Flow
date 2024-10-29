##########################################################################





# Original file copied and modified from     
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
        pass
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
        self.valid_stages = ["synth","floorplan","global_place","detail_place","cts","global_route","detail_route"]
        if not all(k in self.valid_stages for k in self.config.keys()):
            self.logger.error(f"Input YML file must contain options for all stages of the flow: {valid_stages}")
        
        self.flow = []
        for k, v in self.config.items():
            if v["tool"] == "openroad":
                run_cmds, _ = self.orfs_stage(k)
                self.flow.append(run_cmds)
            else:
                # TODO support for external tools
                _, package_cmd = self.orfs_stage(k)
                self.flow.append(package_cmd)
                raise NotImplementedError 

    def orfs_stage(self, stage):
        base_cmd = ""
        base_cmd += f"make -f {self.orfs_make} "
        base_cmd += f"FLOW_HOME={self.orfs_flow} "
        base_cmd += f"DESIGN_CONFIG={self.orfs_design_mk} "
        base_cmd += f"WORK_HOME={self.workdir} "
        run_cmds = [(base_cmd + stage, None)]
        run_cmds += [(base_cmd + "handoff", None)]
        # env=os.environ.copy()
        # env["ODB_FILE"] = orfs_results/f"{result}.odb"
        # env["DEF_FILE"] = orfs_results/f"{result}.odb.def"
        # run_script = "run RUN_SCRIPT="+str(self.src_dir/"create_odb.tcl")
        # package_cmd = [(base_cmd + run_script, env)]
        return run_cmds, None #package_cmd

    def run(self):
        for cmds in self.flow:
            for cmd, env in cmds:
                self.logger.info(f"running cmd={cmd}")
                if env is not None:
                    p = subprocess.run(cmd,shell=True,env=env)
                else:
                    p = subprocess.run(cmd,shell=True)
             
    def process_inputs(self):
        # Defaults
        script_dir = Path(__file__).resolve().parent.parent
        current_path = Path.cwd()
        
        parser = argparse.ArgumentParser(prog = "RobustDesignFlow",
                description = '''Robust Design Flow(RDF).''')
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-v", "--verbose", action="store_true",
                help = "Enables verbose mode with detailed information.")
        group.add_argument("-q", "--quiet", action="store_true",
                help = '''Supresses all informational messages and only
                            displays warnings and errors.''')
        parser.set_defaults(func=lambda : parser.print_help())
        parser.add_argument("-t", "--test", action="store_true",
                help = "Enables test mode override of the defaults")                   
        
        parser.add_argument("-c",'--config', type=Path,
                                dest='config', required=True,
                                help = ''' YAML file containing the target flow''')
        
        parser.add_argument("-l", "--log_file", type=Path,
                help = "Log file for run.",dest='log')
        
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
        parser.add_argument("-m", "--custom_make",
                help = '''Point to a custom design make file instead of an exisitng ORFS design''')
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
        self.orfs_make = self.orfs_flow/"Makefile"
        self.orfs_platform = args.platform 
        self.orfs_design = args.design
        self.orfs_design_dir = self.orfs_flow/f"designs/{self.orfs_platform}/{self.orfs_design}"
        self.orfs_design_mk = self.orfs_design_dir/"config.mk"
        self.orfs_results = self.workdir/f"results/{self.orfs_platform}/{self.orfs_design}/base"
        
        if ((args.custom_make is not None) and args.design):
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

        rdf.process_config(args.config)
        self.logger.info(f"Running Job ID: {job_id}")

if __name__ == '__main__':
    rdf = RobustDesignFlow()
    rdf.process_inputs()
    #TODO support for continuing an existing run.
    rdf.run()





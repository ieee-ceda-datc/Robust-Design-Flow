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


    def run(self):
        src_dir = Path("../src")
        orfs_dir = Path("../flow/OpenROAD-flow-scripts")
        orfs_flow = orfs_dir/"flow"
        orfs_make = orfs_flow/"Makefile"
        orfs_platform = "nangate45"
        orfs_design = "gcd"
        orfs_design_mk = orfs_flow/f"designs/{orfs_platform}/{orfs_design}/config.mk"
        orfs_results = self.workdir/f"results/{orfs_platform}/{orfs_design}/base"
        base_cmd = ""
        base_cmd += f"make -f {orfs_make} "
        base_cmd += f"FLOW_HOME={orfs_flow} "
        base_cmd += f"DESIGN_CONFIG={orfs_design_mk} "
        base_cmd += f"WORK_HOME={self.workdir} "
        for stage, results in [#("synth",["1_synth"]),
                                ("floorplan", ["2_floorplan"] ),
                            #    ("place", ["3_3_place_gp","3_place"]),
                            #    ("route", ["5_1_grt","5_2_route","5_route"]),
                            #   ("finish", ["2_floorplan","3_3_place_gp","3_place","5_1_grt","5_2_route","5_route"]),
        ]:
                #["synth", "floorplan", "3_3_place_gp.odb", "place", # TODO need to add the absolute Paths
                #"cts", "5_1_grt.odb", "5_2_route.odb", "route", "finish"]:
                # [ "1_synth.v", "2_floorplan.odb", "3_3_place_gp.odb", "3_place.odb",
                # "4_cts.odb", "5_1_grt.odb", "5_2_route.odb", "5_route.odb", "6_final.odb"]:
            cmd = base_cmd + stage
            self.logger.info(f"running cmd={cmd}")
            p = subprocess.run(cmd,shell=True)
            cmd = [base_cmd + "handoff"]
            self.logger.info(f"running cmd={cmd}")
            p = subprocess.run(cmd,shell=True)
            # for result in results:
            #     old_odb =  orfs_results/f"{result}.odb"
            #     cmd = f"rm {old_odb}"
            #     self.logger.info(f"running cmd={cmd}")
            #     p = subprocess.run(cmd,shell=True)
            #     env=os.environ.copy()
            #     env["ODB_FILE"] = orfs_results/f"{result}_new.odb"
            #     env["DEF_FILE"] = orfs_results/f"{result}.odb.def"
            #     run_script = "run RUN_SCRIPT="+str(src_dir/"create_odb.tcl")
            #     cmd = base_cmd + run_script
            #     self.logger.info(f"running cmd={cmd}")
            #     p = subprocess.run(cmd,shell=True,env=env)


            # for result in results:
            #     cmd = base_cmd + str(orfs_results/f"{result}.odb.v")
            #     p = subprocess.run(cmd,shell=True)
            #     if stage is not "synth":
            #         cmd = base_cmd + str(orfs_results/f"{result}.odb.def")
            #         p = subprocess.run(cmd,shell=True)
            
        # p = subprocess.run("ls -rtl *",
        #                  stdout=subprocess.PIPE,
        #                  stderr=subprocess.STDOUT,
        #                  shell=True)
        print(p)

        pass
 
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
        group.add_argument("-d", "--debug", action="store_true",
                help = '''Displays additional debug messages for 
                            software debug. Warning: This can lead to 
                            significant increase in messages.''')
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
        args = parser.parse_args()

        if ((not args.test) and args.proceed and args.job_id is None):
            parser.error("--proceed requires --job_id be set to continue an existing job.")

        if args.verbose:
            severity = 'INFO'
        elif args.quiet:
            severity = 'WARNING'
        elif args.debug:
            severity = 'DEBUG'
        else:
            severity = None
        self.logger = self.create_logger( log_file = args.log,
                                        severity = severity)

        config_yml = args.config

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
        self.logger.info(f"Running Job ID: {job_id}")

if __name__ == '__main__':
    
    
    

    rdf = RobustDesignFlow()
    rdf.process_inputs()
    # rdf.process_config()
    # rdf.write_run_scripts()
    #TODO support for continuing an existing run.
    rdf.run()





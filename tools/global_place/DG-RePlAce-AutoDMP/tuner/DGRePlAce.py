from dataclasses import make_dataclass, fields, asdict
from operator import itemgetter
import os
import copy
import json
from pathlib import Path
import logging
import ConfigSpace as CS
import ConfigSpace.hyperparameters as CSH
from ConfigSpace.read_and_write import json as CS_JSON
import random
from Params import Params
import subprocess
import threading

class DGRePlAce:
    def __init__(self, params):
        self.params = Params()
        self.update_params(params, "")
        self.density = 0.0
        self.max_num_level = 2
        self.rsmt = 0.0
        self.hpwl = 0.0
        self.congestion = 0.0
        self.objective = 0.0
        self.overflow = 0.0
        self.max_density = 0.0
        self.niter = 0
        self.coarsening_ratio = 20
        self.halo_width = 2.0
        self.virtualIter = 4
        self.numHops = 4
        #replace your openroad exe here
        self.exe = os.getcwd() + "/OpenROAD-tool/build/src/openroad"
        self.template_file = ""

    def setup_rawdb(self):
        print("Setting up DG-RePlAce rawdb")

    def parseLogFile(self, filename):
        if (not os.path.exists(filename)):
            print("Error Code 100: ", filename, " does not exist")
            return
        
        with open(filename, 'r') as file:
            content = file.read().splitlines()
        file.close()

        worstConH = 1e9
        worstConV = 1e9

        for i in range(len(content) - 1, 1, -1):
            line = content[i]
            if "RSMT wirelength" in line:
                self.rsmt = float(line.split()[-1])
            elif "HPWL wirelength" in line:
                self.hpwl = float(line.split()[-1])
            elif "worstConH" in line:
                worstConH = float(line.split()[-1][:-1])
            elif "worstConV" in line:
                worstConV = float(line.split()[-1][:-1])
            elif "Finished with Overflow" in line:
                self.overflow = float(line.split()[-1])
            elif "Iter:" in line:
                self.niter = int(line.split()[2])
                break

        print("rsmt = ", self.rsmt)
        print("hpwl = ", self.hpwl)
        print("worstConH = ", worstConH)
        print("worstConV = ", worstConV)
        print("overflow = ", self.overflow)
        print("niter = ", self.niter)
        self.congestion = max(worstConH, worstConV)

    def run(self, work_dir):
        print("Running DG-RePlAce")
        print("template_file = ", self.template_file)
    
        self.density = float(self.params.target_density)
        self.max_num_level = float(self.params.max_num_level)
        self.coarsening_ratio = float(self.params.coarsening_ratio)
        self.halo_width = float(self.params.halo_width)
        self.virtualIter = float(self.params.virtualIter)
        self.numHops = float(self.params.numHops)    

        print("density = ", self.density)
        print("max_num_level = ", self.max_num_level)
        print("coarsening_ratio = ", self.coarsening_ratio)
        print("halo_width = ", self.halo_width)
        print("virtualIter = ", self.virtualIter)
        print("numHops = ", self.numHops)

        with open(self.template_file, 'r') as file:
            content = file.read()

        content = content.replace("__density__", str(self.density))
        content = content.replace("__max_num_level__", str(int(self.max_num_level)))
        content = content.replace("__coarsening_ratio__", str(int(self.coarsening_ratio)))
        content = content.replace("__halo_width__", str(self.halo_width))
        content = content.replace("__virtualIter__", str(int(self.virtualIter)))
        content = content.replace("__numHops__", str(int(self.numHops)))

        with open(self.template_file, 'w') as file:
            file.write(content)

        pwd = os.getcwd()
        os.chdir(work_dir)


        self.rsmt = 1e9
        self.hpwl = 1e9
        self.congestion = 1e9
        self.objective = 1e9
        self.overflow = 1e9
        self.max_density = 1e9
        self.niter = 5000

        log_file = self.template_file + ".log"
        cmd = self.exe + "  " + self.template_file + " | tee " + log_file
        print("cmd = ", cmd)

        def target():
            print(log_file)
            os.system(cmd)
            self.parseLogFile(log_file)
            
        thread = threading.Thread(target=target)
        thread.start()

        # Wait for the thread to complete or timeout after 30 minutes (1800 seconds)
        thread.join(timeout=3600)

        if thread.is_alive():
            print("The command timed out after 30 minutes.")
            # Here you can implement additional logic to terminate the command if needed
            # Note: os.system does not provide an easy way to terminate the process,
            # so you might need to use platform-specific methods to kill the process

        os.chdir(pwd)

        final_ppa = {
            "rsmt": self.rsmt,
            "hpwl": self.hpwl,
            "congestion": self.congestion,
            "density": self.density,
        }
        
        other_metrics = {
            "iteration": self.niter,
            "objective": -1 if self.niter == 0 else self.hpwl,
            "overflow": -1 if self.niter == 0 else self.overflow,
            "max_density": -1 if self.niter == 0 else self.overflow,
        }
        
        final_ppa.update(other_metrics)
        logging.info(f"Final PPA: {final_ppa}")

        if (self.rsmt == 1e9 or self.hpwl == 1e9 or self.congestion == 1e9 or self.density == 1e9):
           print("Error: DG-RePlAce failed to run")
        
        return final_ppa      


    def update_params(self, new_params, template_file):
        self.params.update(new_params)
        self.template_file = template_file
        logging.info("parameters = %s" % (self.params))
        
    

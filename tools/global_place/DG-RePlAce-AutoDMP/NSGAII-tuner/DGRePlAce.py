import os
import copy
import json
from pathlib import Path
import logging
import random
import subprocess
import threading
import time
import multiprocessing


def run_command(cmd):
    # run command
    print(cmd)
    os.system(cmd)


class Worker:
    def __init__(self):
        self.rsmt = 0.0
        self.hpwl = 0.0
        self.congestion = 0.0
        self.overflow = 0.0
        self.niter = 0
        self.density = 0.65
        self.coarsening_ratio = 20
        self.halo_width = 2.0
        self.init_bloat_factor = 1.0
        self.density_penalty_coef = 0.99
        self.virtual_iter = 4
        self.num_hops = 4
        self.max_num_level = 2
        self.exe = ""
        self.template_file = ""
        self.design_dir = ""

    def parseLogFile(self, filename):
        print("file_name = ", filename)
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

    # accessor methods
    def set_template_file(self, template_file):
        self.template_file = template_file
    
    def set_target_density(self, target_density):
        self.density = target_density
    
    def set_density_penalty_coef(self, density_penalty_coef):
        self.density_penalty_coef = density_penalty_coef

    def set_halo_width(self, halo_width):
        self.halo_width = halo_width
    
    def set_coarsening_ratio(self, coarsening_ratio):
        self.coarsening_ratio = coarsening_ratio

    def set_max_num_level(self, max_num_level):
        self.max_num_level = max_num_level
    
    def set_virtual_iter(self, virtual_iter):
        self.virtual_iter = virtual_iter
    
    def set_num_hops(self, num_hops):
        self.num_hops = num_hops

    def set_init_bloat_factor(self, init_bloat_factor):
        self.init_bloat_factor = init_bloat_factor
    
    def set_exe(self, exe):
        self.exe = exe

    def set_design_dir(self, design_dir):
        self.design_dir = design_dir



    def run(self, work_dir):
        print("Running DG-RePlAce")
        print("design_dir = ", self.design_dir)
        print("exe = ", self.exe)
        print("template_file = ", self.template_file)
        print("density = ", self.density)
        print("max_num_level = ", self.max_num_level)
        print("coarsening_ratio = ", self.coarsening_ratio)
        print("halo_width = ", self.halo_width)
        print("density_penalty_coef = ", self.density_penalty_coef)
        print("virtual_iter = ", self.virtual_iter)
        print("num_hops = ", self.num_hops)
        print("init_bloat_factor = ", self.init_bloat_factor)

        with open(self.template_file, 'r') as file:
            content = file.read()

        content = content.replace("__design_dir__", self.design_dir)
        content = content.replace("__density__", str(self.density))
        content = content.replace("__max_num_level__", str(int(self.max_num_level)))
        content = content.replace("__coarsening_ratio__", str(int(self.coarsening_ratio)))
        content = content.replace("__halo_width__", str(self.halo_width))
        content = content.replace("__density_penalty_coef__", str(self.density_penalty_coef))
        content = content.replace("__virtualIter__", str(int(self.virtual_iter)))
        content = content.replace("__numHops__", str(int(self.num_hops)))
        content = content.replace("__init_bloat_factor__", str(self.init_bloat_factor))

        with open(self.template_file, 'w') as file:
            file.write(content)

        #pwd = os.getcwd()
        #os.chdir(work_dir)

        self.rsmt = 1e9
        self.hpwl = 1e9
        self.congestion = 1e9
        self.overflow = 1e9
        self.niter = 5000
        self.congestionV = 1e9
        self.congestionH = 1e9

        log_file = self.template_file + ".log"
        cmd = self.exe + "  " + self.template_file + " | tee " + log_file
        print("cmd = ", cmd)


        # create run.sh
        run_sh_file = work_dir + "/run.sh"
        f = open(run_sh_file, "w")
        line = "module unload anaconda3/5.0.1\n"
        line += "module unload gcc/9.3.0\n"
        line += "module load gcc/9.3.0\n"
        line += "module unload cmake/3.16.2\n"
        line += "module load cmake/3.25.1\n"
        line += "module unload tcl/8.6.6\n"
        line += "module load tcl/8.5.13\n"
        line += "module load cuda/12.2\n"
        line += "module unload boost/1.78.0\n"
        line += "module load boost/1.81.0\n"
        line += "nvidia-smi\n"
        line += cmd + "\n"
        f.write(line)
        f.close()
        os.system("chmod +x " + run_sh_file)
        cmd = "source " + run_sh_file
        #os.system(cmd)

        p = multiprocessing.Process(target=run_command, name = "run_command", args=(cmd, ))
        p.start()
        p.join(3600 * 12)
        p.kill()
    

        """
        def target():
            print(log_file)
            os.system(cmd)
            time.sleep(1)
            self.parseLogFile(log_file)
            
        thread = threading.Thread(target=target)
        thread.start()

        # Wait for the thread to complete or timeout after 30 minutes (1800 seconds)
        thread.join(timeout=3600 * 24 * 3)

        if thread.is_alive():
            print("The command timed out after 30 minutes.")
            # Here you can implement additional logic to terminate the command if needed
            # Note: os.system does not provide an easy way to terminate the process,
            # so you might need to use platform-specific methods to kill the process

        #os.chdir(pwd)
        """
        self.parseLogFile(log_file)

        if (self.rsmt == 1e9 or self.hpwl == 1e9 or self.congestion == 1e9 or self.density == 1e9):
           print("Error: DG-RePlAce failed to run")
        
        return self.rsmt, self.congestion, self.density  
        
    

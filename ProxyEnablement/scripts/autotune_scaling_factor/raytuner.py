################################################################################
# Author: Sayak Kundu and Dooseok Yoon                                         #
# email: sakundu [at] ucsd [dot] edu and d3yoon [at] ucsd [dot] edu            #
# It run autotuning for scaling factor using raytune to reduce the PPA gap     #
# between a target (golden) library and asap7.                                 #
################################################################################

import time
import os
import numpy as np
import re
from extract_scaled_loss import extract_scale_loss
from datetime import datetime
from ray import tune, train
from ray.tune.search import ConcurrencyLimiter
from ray.tune.schedulers import AsyncHyperBandScheduler
from ray.tune.search.hyperopt import HyperOptSearch

file_path = os.path.abspath(__file__)
proj_dir = re.search(r'/\S+/ProxyEnablement', file_path).group(0)
PROJ_DIR = os.environ.get('PROJ_DIR', proj_dir)

class raytune:
    def autotuneObjective(self, config):
        scaling_factor = [config.get('delayScale_RVT'),
                          config.get('delayScale_LVT'),
                          config.get('delayScale_SLVT'),
                          config.get('PowerScale_RVT'),
                          config.get('PowerScale_LVT'),
                          config.get('PowerScale_SLVT'),
                          config.get('constScale_RVT'),
                          config.get('constScale_LVT'),
                          config.get('constScale_SLVT'),
                          config.get('pinCapScale_RVT'),
                          config.get('pinCapScale_LVT'),
                          config.get('pinCapScale_SLVT'),
                          config.get('metalCapScale'),
                          config.get('metalResScale')]
        
        loss, max_loss, std_loss = extract_scale_loss(scaling_factor,
                                                      self.tcp_list, self.util,
                                                      self.ref_dir,
                                                      self.ref_csv)
        
        train.report({"loss": loss, "max_loss": max_loss, "std_loss": std_loss})

    def __init__(self, num_samples, num_jobs):
        ## Ensure tcp_list and util list are same as in the golden report ##
        self.tcp_list = [667.0, 566.0, 516.0, 457.0, 410.0, 383.0, 330.0, 288.0, 272.0]
        self.util = [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7]
        ## Set ref_dir as the project directory ##
        self.ref_dir = PROJ_DIR
        
        ## CSV file of the Golden data ##
        # The required columns are testcase, target_util, tcp, core_area,
        # std_cell_area, worst_neg_slack, effective_clock_period, 
        # internal_power, switching_power, leakage_power, total_power
        self.ref_csv = f"{PROJ_DIR}/benchmarks/jpeg_encoder/golden_sample.csv"
        self.num_samples = num_samples
        self.num_jobs = num_jobs # number of cpus used by tune
        self.config = {
            # ------- general parameters ------------*
            "delayScale_RVT":           tune.quniform(-0.4, 0.4, 0.01),
            "delayScale_LVT":           tune.quniform(-0.4, 0.4, 0.01),
            "delayScale_SLVT":          tune.quniform(-0.4, 0.4, 0.01),
            "PowerScale_RVT":           tune.quniform(-0.3, 0.3, 0.01),
            "PowerScale_LVT":           tune.quniform(-0.3, 0.3, 0.01),
            "PowerScale_SLVT":          tune.quniform(-0.3, 0.3, 0.01),
            "constScale_RVT":           tune.quniform(-0.4, 0.4, 0.01),
            "constScale_LVT":           tune.quniform(-0.4, 0.4, 0.01),
            "constScale_SLVT":          tune.quniform(-0.4, 0.4, 0.01),
            "pinCapScale_RVT":          tune.quniform(0.5, 1.5, 0.01),
            "pinCapScale_LVT":          tune.quniform(0.5, 1.5, 0.01),
            "pinCapScale_SLVT":         tune.quniform(0.5, 1.5, 0.01),
            "metalCapScale":          tune.quniform(0.5, 1.5, 0.05),
            "metalResScale":         tune.quniform(0.5, 1.5, 0.05),
            }
        self.algo = HyperOptSearch()
        
        # User-defined concurrent #runs
        self.algo = ConcurrencyLimiter(self.algo, max_concurrent= self.num_jobs)
        self.scheduler = AsyncHyperBandScheduler()

    def __call__(self):
        start = time.time()
        analysis = tune.run(
            self.autotuneObjective,
            metric="loss",
            mode="min",
            search_alg=self.algo,
            scheduler=self.scheduler,
            num_samples=self.num_samples,
            config=self.config,
            storage_path="%s" % (os.getcwd()),
        )
        end = time.time()
        runtime = round(end - start, 3)
        best_loss = analysis.best_result.get('loss')
        best_max_loss = analysis.best_result.get('max_loss')
        best_std_loss = analysis.best_result.get('std_loss')
        best_config = analysis.best_config
        print(f"Runtime: {runtime}")
        print(f"Best config: {best_config}")
        print(f"Best loss: {best_loss}, Best max loss: {best_max_loss}, "
              f"Best std loss: {best_std_loss}")
        
if __name__ == '__main__':
    num_samples = 5
    num_jobs = 1
    raytune = raytune(num_samples, num_jobs)
    raytune()

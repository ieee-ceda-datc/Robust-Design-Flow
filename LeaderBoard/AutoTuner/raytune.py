import os
import sys
import optuna
import random
from ray import tune, train
from run_or_job import run_job
from ray.tune.search import ConcurrencyLimiter
from ray.tune.search.optuna import OptunaSearch
from ray.tune.schedulers import ASHAScheduler, AsyncHyperBandScheduler

def get_search_space(design, run_dir, tech="nangate45"):
    if tech == "nangate45":
        clk_period = tune.uniform(0.1, 10.0)
    else:
        clk_period = tune.uniform(100, 10000)
    
    search_space = {
        "design": design,
        "tech": tech,
        "run_dir": run_dir,
        "clk_period": clk_period,
        "util": tune.uniform(30, 99.99),
        "ar": 1,
        "density_lb_addon": tune.uniform(0.0, 0.99),
        "timing_effort": tune.choice(range(101)),
        "power_effort": tune.choice(range(101)),
        "is_hier": tune.choice([0, 1]),
        "gp_pad": tune.choice([x for x in range(0, 3)]),
        "dp_pad": tune.choice([x for x in range(0, 3)]),
        "enable_dpo": tune.choice([0, 1]),
        "cts_cluster_size": tune.choice([x for x in range(10, 200)]),
        "cts_cluster_dia": tune.choice([x for x in range(20, 400)]),
        "gp_rd": tune.choice([0, 1]),
        "gp_td": tune.choice([0, 1]),
        "pin_adj": tune.uniform(0.1, 0.8),
        "up_adj": tune.uniform(0.1, 0.8)
    }
    return search_space

class rayTune():
    def __init__(self, design:str):
        self.design = design
        self.sample_id_counter = 0
        
    def objective(self, config):
        design = config["design"]
        clk_period = round(config["clk_period"], 3)
        util = round(config["util"], 3)
        ar = round(config["ar"], 3)
        tech = config["tech"]
        density_lb_addon = round(config["density_lb_addon"], 3)
        timing_effort = config["timing_effort"]
        power_effort = config["power_effort"]
        is_hier = config["is_hier"]
        gp_pad = config["gp_pad"]
        dp_pad = config["dp_pad"]
        enable_dpo = config["enable_dpo"]
        cts_cluster_size = config["cts_cluster_size"]
        cts_cluster_dia = config["cts_cluster_dia"]
        gp_rd = config["gp_rd"]
        gp_td = config["gp_td"]
        pin_adj = round(config["pin_adj"], 3)
        up_adj = round(config["up_adj"], 3)
        
        run_dir = config["run_dir"]
        self.sample_id_counter += 1
        servers = ["npc", "opc", "dpl", "gpl", "hgr", "eda", "lvs", "pdn", "dme", "soi"]
        server = random.choice(servers)
        ## Please provide the correct path for the cached netlist
        cached_netlist = f"xx/{design}_{tech}_{self.obj}"
        ppa = run_job(design, clk_period, util, ar, tech, density_lb_addon,
                timing_effort, is_hier, power_effort, gp_pad, dp_pad,
                enable_dpo, cts_cluster_size, cts_cluster_dia, gp_rd, gp_td,
                pin_adj, up_adj, run_dir, server)
        
        if ppa[3] > 50:
            train.report({"power":float("inf"), "performance":float('inf'),
                        "area":float("inf"), "Step": self.sample_id_counter})
        else:
            train.report({"power":ppa[0], "performance": ppa[1], "area": ppa[2],
                        "Step": self.sample_id_counter})

    def __call__(self, tech="ng45", obj="area"):
        ## set run_directory where you want to run your autotuner job
        run_dir=""
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
            
        search_space = get_search_space(f"{self.design}", run_dir, tech)
        self.obj = obj
        self.tech = tech
        # optuna_search = OptunaSearch(
        #     metric=["power", "performance", "area"],
        #     mode=["min", "min", "min"],  # Minimizing all objectives
        # )
        
        optuna_search = OptunaSearch(metric=obj, mode="min")

        algo = ConcurrencyLimiter(optuna_search, max_concurrent=8)
        scheduler = AsyncHyperBandScheduler(metric=obj, mode="min", max_t=14400)

        # Profile a correct path for the log_dir
        log_dir = f"xx"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        analysis = tune.run(
            self.objective,
            search_alg=algo,
            scheduler=scheduler,
            num_samples=600,
            config=search_space,
            progress_reporter=tune.CLIReporter(metric_columns=[obj]),
            name=f"{self.design}_{tech}_{obj}",
            storage_path=log_dir,
            log_to_file=True,
        )

design=sys.argv[1]
tech=sys.argv[2]
obj=sys.argv[3]
r = rayTune(design)
r(tech, obj)
# Extract the best trials from the Pareto front
# python raytune.py aes asap7 area
# 

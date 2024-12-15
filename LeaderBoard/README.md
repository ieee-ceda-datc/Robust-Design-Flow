# Leader Board
Here, we provide the AutoTuner [script](./AutoTuner) to tune the hyperparameters of OpenROAD-flow-scripts for the AES, Ibex, and JPEG designs on the Nangate45 enablement, as mentioned in the [RDF-2024
paper](https://vlsicad.ucsd.edu/Publications/Conferences/412/c412.pdf) paper. Additionally, we provide the [baseline solutions](./designs) reported in the RDF-2024 paper. 
  

We have also shared the [evaluation script](./AutoTuner/run_eval.sh) to evaluate your results using our flow.

## AutoTuner
To run AutoTuner, you need to use the [raytune.py](./AutoTuner/raytune.py) file. Before running [raytune.py](./AutoTuner/raytune.py), please make the following changes:

1. Update `MAKE_HOME` in [run_or_job.sh](./AutoTuner/run_or_job.sh) with the full path to the OpenROAD-flow-scripts/flow directory.
2. Update `run_dir` in the [raytune.py](./AutoTuner/raytune.py) file with the path where you want to run your AutoTuner script.
3. If you are running AutoTuner for a synthesized netlist, please provide the `cached_netlist` file path in the [raytune.py](./AutoTuner/raytune.py) file (Line 70).

We assume that you have installed [RayTune](https://docs.ray.io/en/latest/ray-overview/installation.html), [Optuna](https://optuna.readthedocs.io/en/stable/installation.html), and [OpenROAD-flow-scripts](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts?tab=readme-ov-file#tool-installation) on your system. If not, you can click on each item and follow the installation steps.

Before launching the AutoTuner run, ensure that you have set the hyperparameter ranges correctly in [raytune.py](./AutoTuner/raytune.py). Once done, you can launch your job using the following commands:

```bash
cd ./AutoTuner
python3 raytune.py
```

## Running Evaluation
We assume that you have a routed DEF file and an SDC file. To run the evaluation, please follow these steps:
```bash
cd ./AutoTuner
## Designs name are aes, ibex and jpeg
## If you plan to run other designs please create a config file for that design
./run_eval.sh <DEF Path> <SDC PATH> <DESIGN NAME>
```

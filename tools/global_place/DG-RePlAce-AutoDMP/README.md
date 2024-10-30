# DG-RePlAce Parameter Autotuner 

* Built upon the GPU-accelerated global placer [DG-RePlAce](https://arxiv.org/abs/2404.13049) and the [OpenROAD](https://github.com/The-OpenROAD-Project) project.
* Automatic parameter tuning based on the multi-objective hyperparameter Bayesian optimization (MOTPE) algorithm from [AutoDMP](https://github.com/NVlabs/AutoDMP).
* Automatic parameter tuning based on the NSGA-II algorithm from [Ray Tune](https://optuna.readthedocs.io/en/v2.0.0/reference/multi_objective/generated/optuna.multi_objective.samplers.NSGAIIMultiObjectiveSampler.html).

## Description ##
This repository supports the goal of "multi-variable, multi-objective autotuning" for the GPU-accelerated global placer (DG-RePlAce) within the OpenROAD platform. It harnesses GPU computational power to enhance the PPA (Power, Performance, and Area) of open-source EDA tools. This repository serves the following purposes:

* We provide the source code for the GPU-accelerated RePlAce [OpenROAD-tool/src/gpl2](https://github.com/ABKGroup/DG-RePlAce-AutoDMP/tree/main/OpenROAD-tool/src/gpl2), which is fully integrated within the OpenROAD RTL-to-GDSII flow, and implemented in CUDA and C++
to eliminate dependencies on external frameworks such as PyTorch.

* We adapt the MOTPE-based tuning framework from [AutoDMP](https://github.com/NVlabs/AutoDMP) to tune the parameters for our GPU-accelerated RePlAce. [code](https://github.com/ABKGroup/DG-RePlAce-AutoDMP/tree/main/tuner)

* We porvide the NSGA-II-based tuning framework to tune the parameters for our GPU-accelerated RePlAce. [code](https://github.com/ABKGroup/DG-RePlAce-AutoDMP/tree/main/NSGAII-tuner)

We hope to see pull requests with new testcases and optimization codes,  and will continue to update the repository as this happens.


## Dependency and Installation ##
- Refer to the [OpenROAD](https://github.com/the-openroad-project) project for instructions on installing OpenROAD.
- Refer to the [AutoDMP](https://github.com/NVlabs/AutoDMP) project for the AutoDMP dependency.
- Refer to the [Ray Tune](https://docs.ray.io/en/latest/tune/index.html) for instructions on installing Ray Tune.
- CUDA Version >= 11.8
    - The code has been tested on GPUs with compute compatibility 8.0 on DGX A100 machine. 


## How to Run Multi-Objective Bayesian Optimization ##

To run the multi-objective Bayesian optimization framework on the [swerv_wrapper](https://github.com/ABKGroup/DG-RePlAce-AutoDMP/tree/main/test/swerv_wrapper), execute:
```
source run_me.sh
```
For details on each parameter, please refer to the [AutoDMP](https://github.com/NVlabs/AutoDMP) project.


## How to Run NSGA-II Optimization ##
To run the NSGA-II framework on the [swerv_wrapper](https://github.com/ABKGroup/DG-RePlAce-AutoDMP/tree/main/test/swerv_wrapper), execute:
```
cd NSGAII-tuner && python tune_NSGAII.py
```
For details on each parameter, please refer to the [tune_NSGAII.py](https://github.com/ABKGroup/DG-RePlAce-AutoDMP/blob/main/NSGAII-tuner/tune_NSGAII.py).

## References ##
To reference this work, please cite:

A. B. Kahng and Z. Wang, "DG-RePlAce: A Dataflow-Driven GPU-Accelerated Analytical Global Placement Framework for Machine Learning Accelerators", 
*IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*, 2024.

V. A. Chhabria, V. Gopalakrishnan, A. B. Kahng, S. Kundu, Z. Wang, B.-Y. Wu and D. Yoon, "Strengthening the Foundations of IC Physical Design and ML EDA Research", 
*Proc. International Conference on Computer-Aided Design*, 2024.




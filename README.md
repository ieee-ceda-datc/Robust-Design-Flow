# Robust Design Flow

## Proxy Enablements
Please install the following packages in your conda environment to run the library scaling flow:
1. liberty parser: `pip install liberty-parser`
2. ray: `pip install ray[tune]`
  

To run the library scaling flow, please follow the steps below:
1. First update the range of different scaling parameters [here](./ProxyEnablement/scripts/autotune_scaling_factor/raytuner.py#L63-L76).
2. Provide the PPA number of the benchmark design on the target library [here](./ProxyEnablement/scripts/autotune_scaling_factor/raytuner.py#L58).
3. Update total number of samples and number of parallel jobs to use for the autotuning job [here](./ProxyEnablement/scripts/autotune_scaling_factor/raytuner.py#L108-L109).
4. Add the target clock periods and utilization list based on the golden data [here](./ProxyEnablement/scripts/autotune_scaling_factor/raytuner.py#L49-L50).
5. Additoinally, if you plan to use multiple servers to run SP&R jobs in parallel using [GNU paralle](https://www.gnu.org/software/parallel/), please update the [node](./ProxyEnablement/scripts/util/node) file and its path [here](./ProxyEnablement/scripts/autotune_scaling_factor/extract_scaled_loss.py#L115).
6. Use the following command in your python environment to run the autotuning flow:
```
export PROJ_DIR=<path to the root directory of this repository>
python ./ProxyEnablement/scripts/autotune_scaling_factor/raytuner.py

```

At the end of the run you will get the best scaling parameters for the given benchmark design that minimizes the PPA differece with the target library. You can find all the scaled libraries in the following path:
```
./ProxyEnablement/run/libraries/scaled_lib_<scaling_factor>
```


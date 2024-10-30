# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# AutoDMP base config
AUTODMP_BASE_CONFIG = {
    "aux_input": "",
    "lef_input": "",
    "def_input": "",
    "verilog_input": "",
    "gpu": 0,
    "gpu_id": 0,
    "target_density": 0.7,
    "max_num_level": 2,
    "coarsening_ratio": 10,
    "halo_width": 1,
    "virtualIter": 10,
    "numHops": 4,
}

# Cost ratio for unfinished AutoDMP runs
AUTODMP_BAD_RATIO = 10


# Base PPA: HPWL, RSMT, Congestion, Density
AUTODMP_BASE_PPA = {
    "nvdla_asap7": {
        "hpwl": 1.37e9,
        "rsmt": 1.62e9,
        "congestion": 0.60,
        "density": 0.70,
    },
}

AUTODMP_BEST_CFG = {
    "nvdla_asap7": {
        "target_density": 0.7037918984939342,
        "max_num_level": 2,
        "coarsening_ratio": 10,
        "halo_width": 1,
        "virtualIter": 10,
        "numHops": 4,
    },
}


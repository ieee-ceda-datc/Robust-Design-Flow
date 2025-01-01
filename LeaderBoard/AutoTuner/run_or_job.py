import os
import sys
import json
import subprocess


def extract_ppa(log_dir:str, clk:float) -> Tuple[float, float, float, float]:
    rpt_file=f"{log_dir}/6_report.json"
    # Parse the JSON data
    if os.path.exists(rpt_file):
        fp = open(rpt_file, 'r')
        data = json.loads(fp.read().strip())
        fp.close()
        
        # Extract the required fields
        ws = float(data.get("finish__timing__setup__ws"))
        core_area = float(data.get("finish__design__core__area"))
        total_power = float(data.get("finish__power__total"))
        fp = open(f"{log_dir}/5_3_route.json", 'r')
        drc_data = json.loads(fp.read().strip())
        fp.close()
        drc_count = float(drc_data.get("detailedroute__route__drc_errors"))
        return total_power, clk - ws, core_area, drc_count

    return float('inf'), float('inf'), float('inf'), float('inf')

def get_job_name(design:str, clk_period:float, util:float, ar:float, tech:str,
                density_lb_addon:float, timing_effort:int, is_hier:int,
                power_effort:int, gp_pad:int, dp_pad:int, enable_dpo:int,
                cts_cluster_size:int, cts_cluster_dia:int, gp_rd:int, gp_td:int,
                pin_adj:float, up_adj:float) -> str:
    job_name=f"DESIGN_{design}__CLK_{clk_period}__UTIL_{util}"\
            f"__AR_{ar}__TECH_{tech}__"\
            f"LB_ADDON_{density_lb_addon}__TIMING_EFFORT_{timing_effort}"\
            f"__POWER_EFFORT_{power_effort}__HIER_SYNTH_{is_hier}"\
            f"__GP_PAD_{gp_pad}__DP_PAD_{dp_pad}__RD_{gp_rd}__TD_{gp_td}"\
            f"__DPO_{enable_dpo}__CTS_CSIZE_{cts_cluster_size}"\
            f"__CTS_CDIA_{cts_cluster_dia}__PIN_ADJ_{pin_adj}__UP_ADJ_{up_adj}"
    return job_name

def run_job(design:str, clk_period:float, util:float, ar:float, tech:str,
            density_lb_addon:float, timing_effort:int, is_hier:int,
            power_effort:int, gp_pad:int, dp_pad:int, enable_dpo:int,
            cts_cluster_size:int, cts_cluster_dia:int, gp_rd:int, gp_td:int,
            pin_adj:float, up_adj:float, run_dir:str, server:str,
            cached_netlist:Optional[str] = None, timeout:int = 14400) -> Tuple[float, float, float, float]:
    ref_dir=os.path.dirname(os.path.abspath(__file__))
    ref_script=f"{ref_dir}/run_or_job.sh"
    dq='"'
    if cached_netlist is not None and os.path.exists(cached_netlist):
        run_dir_b = f"{run_dir} {cached_netlist}"
    else:
        run_dir_b = run_dir
    shell_command = f"ssh {server} {dq}{ref_script} {design} {clk_period}"\
                    f" {util} {ar} {tech} {density_lb_addon}"\
                    f" {timing_effort} {power_effort} {is_hier} {gp_pad}"\
                    f" {dp_pad} {enable_dpo} {gp_td} {gp_rd}"\
                    f" {cts_cluster_size} {cts_cluster_dia} {pin_adj}"\
                    f" {up_adj} {run_dir_b}{dq}"
    job_name=get_job_name(design, clk_period, util, ar, tech, density_lb_addon,
                        timing_effort, is_hier, power_effort, gp_pad, dp_pad,
                        enable_dpo, cts_cluster_size, cts_cluster_dia, gp_rd,
                        gp_td, pin_adj, up_adj)
    
    print(f"Running: {shell_command}")
    
    if design == "aes_cipher_top":
        design_name = "aes"
    elif design == "ibex_core":
        design_name = "ibex"
    elif design == "jpeg_encoder":
        design_name = "jpeg"
    else:
        design_name = design
    
    try:
        _ = subprocess.run(shell_command, timeout=timeout, shell=True,
                           check=True, stdout=subprocess.DEVNULL)
        return extract_ppa(f"{run_dir}/logs/{tech}/{design_name}/{job_name}",
                clk_period)
    except subprocess.TimeoutExpired:
        print(f"Timeout: {timeout} seconds")
        return float('inf'), float('inf'), float('inf'), float('inf')
    except subprocess.CalledProcessError as error_message:
        print(f"Error: {error_message}")
        return float('inf'), float('inf'), float('inf'), float('inf')
    
if __name__ == "__main__":
    run_dir=""
    design="jpeg"
    clk_period=500.0
    util=30
    ar=1.0
    tech="nangate45"
    density_lb_addon=0.20
    timing_effort=5
    is_hier=0
    power_effort=5
    gp_pad=1
    dp_pad=0
    enable_dpo=1
    cts_cluster_size=32
    cts_cluster_dia=50
    gp_rd=1
    gp_td=1
    pin_adj=0.3
    up_adj=0.6
    server="dpl"
    cached_netlist=None
    
    a = run_job(design, clk_period, util, ar, tech, density_lb_addon,
                timing_effort, is_hier, power_effort, gp_pad, dp_pad,
                enable_dpo, cts_cluster_size, cts_cluster_dia, gp_rd, gp_td,
                pin_adj, up_adj, run_dir, server, cached_netlist)
    
    print(a)

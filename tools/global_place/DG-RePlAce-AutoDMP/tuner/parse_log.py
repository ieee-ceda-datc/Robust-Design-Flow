import os

def parseLogFile(filename):
    with open(filename, 'r') as file:
        content = file.read().splitlines()
    file.close()

    rsmt = 1e9
    hpwl = 1e9
    congestion = 1e9
    objective = 1e9
    overflow = 1e9
    niter = 5000
    worstConH = 1e9
    worstConV = 1e9

    for i in range(len(content) - 1, 1, -1):
        line = content[i]
        if "RSMT wirelength" in line:
            rsmt = float(line.split()[-1])
        elif "HPWL wirelength" in line:
            hpwl = float(line.split()[-1])
        elif "worstConH" in line:
            worstConH = float(line.split()[-1][:-1])
        elif "worstConV" in line:
            worstConV = float(line.split()[-1][:-1])
        elif "Finished with Overflow" in line:
            overflow = float(line.split()[-1])
        elif "Iter:" in line:
            niter = int(line.split()[2])
            break

    print("rsmt = ", rsmt)
    print("hpwl = ", hpwl)
    print("worstConH = ", worstConH)
    print("worstConV = ", worstConV)
    print("overflow = ", overflow)
    print("niter = ", niter)


file_name = "/home/dgx_projects/zhiang/AutoDMP-DG-RePlAce/test/nvdla_nangate45_51/mobohb_log/NV_NVDLA_partition_c/run-0_0_1/run.log"
parseLogFile(file_name)

set lib_setup_file ../../../tcl/lib_setup_or.tcl
set design_setup_file ../../../tcl/design_setup.tcl

set stamp1 [clock seconds]
source $lib_setup_file
source $design_setup_file

foreach lef_file ${lefs} {
  read_lef $lef_file
}

foreach lib_file ${libworst} {
  read_liberty $lib_file
}


read_verilog $netlist
link_design $top_design
read_sdc $sdc

read_def $def -floorplan_initialize

set stamp2 [clock seconds]

puts "Time for reading the design into OpenDB and OpenSTA : [expr $stamp2 - $stamp1] second" 

rtl_macro_placer -auto_cluster_only_flag true -max_num_level __max_num_level__ -coarsening_ratio __coarsening_ratio__

set stamp3 [clock seconds]

puts "Time for Autoclustering engine : [expr $stamp3 - $stamp2] second"

gpu_global_placement -density __density__ \
                     -halo_width __halo_width__ \
		     -virtualIter __virtualIter__ \
		     -numHops __numHops__ 
		     #-cluster_constraint_flag \
                     #-datapath_flag -dataflow_flag

set stamp4 [clock seconds]

puts "Time for global placement : [expr $stamp4 - $stamp3] seconds"

write_def gpu.def

set stamp5 [clock seconds]

puts "Time for writing def : [expr $stamp5 - $stamp4] seconds"

detailed_placement

set stamp6 [clock seconds]

puts "Time for detailed placement : [expr $stamp6 - $stamp5] seconds"

set thread [expr [exec getconf _NPROCESSORS_ONLN] / 1]

puts "\[INFO\] Number of threads: $thread"

set_thread_count $thread
detailed_route -output_drc results/nangate45.output.drc.rpt \
               -output_maze results/nangate45.output.maze.log \
               -verbose 1

set stamp7 [clock seconds]

puts "Time for evaluation : [expr $stamp7 - $stamp6] seconds"


puts "\[INFO\] Running time:   [expr $stamp7 - $stamp1] second"

exit



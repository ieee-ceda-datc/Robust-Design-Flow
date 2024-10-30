source $::env(SCRIPTS_DIR)/util.tcl
# Read liberty files
source $::env(SCRIPTS_DIR)/read_liberty.tcl

# Read def
if {[env_var_exists_and_non_empty DEF_FILE]} {
    # Read lef
    read_lef $::env(TECH_LEF)
    read_lef $::env(SC_LEF)
    if {[env_var_exists_and_non_empty ADDITIONAL_LEFS]} {
      foreach lef $::env(ADDITIONAL_LEFS) {
        read_lef $lef
      }
    }
    set input_file $::env(DEF_FILE)
    read_def $input_file
    if {[env_var_exists_and_non_empty SDC_FILE]} {
        read_sdc $::env(SDC_FILE)
    }
    write_db $::env(ODB_FILE)
} else {
    puts "Please provide a DEF file"
}


# test for grid with ring
from openroad import Design, Tech
import pdn_aux
import helpers

tech = Tech()
tech.readLef("Nangate45/Nangate45.lef")
design = Design(tech)
design.readDef("nangate_gcd/floorplan.def")

pdn_aux.add_global_connection(design, net_name="VDD", pin_pattern="VDD", power=True)
pdn_aux.add_global_connection(design, net_name="VSS", pin_pattern="VSS", ground=True)

pdn_aux.set_voltage_domain(design, power='VDD', ground='VSS')

pdn_aux.define_pdn_grid_real(design, name="Core")
pdn_aux.add_pdn_stripe(design, followpins=True, layer="metal1", extend_to_core_ring=True)

pdn_aux.add_pdn_ring(design, grid="Core", layers=["metal5", "metal6"], widths=2*[2.0],
                     spacings=2*[2.0], core_offsets=4*[2.0])

pdn_aux.add_pdn_connect(design, layers=["metal5", "metal6"])
pdn_aux.add_pdn_connect(design, layers=["metal1", "metal6"])

pdn_aux.pdngen_db(design)

def_file = helpers.make_result_file("core_grid_with_rings.def")
design.writeDef(def_file)
helpers.diff_files("core_grid_with_rings.defok", def_file)

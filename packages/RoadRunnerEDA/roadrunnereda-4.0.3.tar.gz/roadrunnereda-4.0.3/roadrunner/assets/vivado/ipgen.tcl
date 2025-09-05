set name {<%-ipName%>}
set board {<%-ipBoard%>}
set part {<%-ipPart%>}
set iptype {<%-ipType%>}

create_project -in_memory rrun project

set prj [get_projects rrun]
set_property part $part $prj
if {$part != ""} {
    set_property board_part $board $prj
}
set_property target_language Verilog $prj

create_ip -vlnv $iptype -module_name $name -dir . -force
set ipi [get_ips $name]
set props {}

<% for key,val in pairs(properties) do %>
lappend props <%-key%> <%-val%>
<% end %>

set_property -dict $props $ipi

report_property $ipi

generate_target all $ipi

#generate design check point for synthesis
synth_ip $ipi

set prefix [expr [string length [pwd]] + 1]

proc putlist {fh indent key lst {prefix ""}} {
    if {[llength $lst] != 0} {
        puts $fh "$indent$key:"
        foreach fil $lst {
            if { $prefix != "" } {
                set rel [string range $fil $prefix 1000]
            } else {
                set rel $fil
            }
            puts $fh "$indent  - $rel"
        }
    }
}

proc getlist {ip type scope} {
    set filter ""
    if { $type == "v" } { lappend filter FILE_TYPE == Verilog && name !~ *netlist.v }
    if { $type == "sv" } { lappend filter FILE_TYPE == SystemVerilog }
    if { $type == "vhdl" } { lappend filter FILE_TYPE == VHDL && name !~ *netlist.vhdl && name !~ *stub.vhdl }
    if { $type == "xdc" } { lappend filter FILE_TYPE == XDC }

    if { $scope == "sim" } { lappend filter && USED_IN =~ *simulation* }
    return [get_files -of_object $ip -filter $filter]
}

set fh [open RR w]
puts $fh "top:"
puts $fh "  /default:"
#general info
puts $fh "    name: [get_property NAME $ipi]"
puts $fh "    coreId: [get_property IPDEF $ipi]"
puts $fh "    coreVersion: [get_property CORE_REVISION $ipi]"
puts $fh "    VivadoVersion: \"[get_property SW_VERSION $ipi]\""
puts $fh "    part: [get_property PART $ipi]"

#synthesis
puts $fh "  /SYNTHESIS:"
puts $fh "    ip: [string range [get_property IP_FILE $ipi] $prefix 1000]"
set lst [getlist $ipi xdc all]
if {[llength $lst] != 0} {
    putlist $fh "    " constraints $lst $prefix
}

#design checkpoint
set lst [get_files -of_object $ipi -filter {FILE_TYPE == "Design Checkpoint"}]
if {[llength $lst] != 0} {
    puts $fh "    dcp: [string range $lst $prefix 1000]"
}

#simulation - FIXME invlaid if there are no simulation sources
puts $fh "  /SIMULATION:"
#verilog sources
putlist $fh "    " v [getlist $ipi v sim] $prefix
putlist $fh "    " sv [getlist $ipi sv sim] $prefix
putlist $fh "    " vhdl [getlist $ipi vhdl sim] $prefix
putlist $fh "    " xilinxFeatures {<%-xilinxFeatures%>}
putlist $fh "    " xilinxLibs {<%-xilinxLibs%>}
stepLoad routed.dcp $hasState

logmsg "Design: write_bitstream"
write_bitstream -force <%-toplevel%>.bit

#TODO maybe build a try-catch around
#logmsg "Design: write_debug_probes"
#write_debug_probes -quiet -force {toplevel}
#file copy -force {toplevel}.ltx debug_nets.ltx

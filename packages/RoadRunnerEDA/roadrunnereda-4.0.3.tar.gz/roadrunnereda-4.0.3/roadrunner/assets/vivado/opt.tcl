if {[stepNeeded opt.dcp $incremental] == 0} { return }

logmsg "Load: synth.dcp"
read_checkpoint synth.dcp

logmsg "Design: link"
link_design

logmsg "Design: opt"
opt_design
logmsg "Report: opt.rpt (.pb) DRC"
report_drc -file opt.rpt -pb opt.pb
logmsg "Checkpoint: opt.dcp"
write_checkpoint -force opt.dcp
set hasState 1
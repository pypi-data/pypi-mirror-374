if {[stepNeeded placed.dcp $incremental] == 0} { return }
stepLoad opt.dcp $hasState

logmsg "Design: place_design"
place_design
logmsg "Report: placed_io.rpt (.pb)"
report_drc -file placed_io.rpt -pb placed_io.pb
logmsg "Report: placed_utilization.rpt (.pb)"
report_utilization -file placed_utilization.rpt -pb placed_utilization.pb
logmsg "Report: placed_control_sets.rpt"
report_control_sets -verbose -file placed_control_sets.rpt
logmsg "Checkpoint: placed.dcp"
write_checkpoint -force placed.dcp
set hasState 1
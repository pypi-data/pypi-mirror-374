if {[stepNeeded routed.dcp $incremental] == 0} { return }
stepLoad placed.dcp $hasState

logmsg "Design: route_design"
route_design
logmsg "Reports: routed_*.rpt (.pb) (.rpx)"
report_drc -file placed_io.rpt -pb placed_io.pb
report_drc -file routed_drc.rpt -pb routed_drc.pb -rpx routed_drc.rpx
report_methodology -file routed_methodology_drc.rpt -pb routed_methodology_drc.pb -rpx routed_methodology_drc.rpx
report_power -file routed_power.rpt -pb routed_power.pb -rpx routed_power.rpx
report_route_status -file routed_route_status.rpt -pb routed_route_status.pb
report_timing_summary -max_paths 10 -file routed_timing.rpt -pb routed_timing.pb -rpx routed_timing.rpx -warn_on_violation
report_incremental_reuse -file routed_incremental_reuse.rpt
report_clock_utilization -file routed_clock_utilization.rpt
report_bus_skew -warn_on_violation -file routed_bus_skew.rpt -pb routed_bus_skew.pb -rpx routed_bus_skew.rpx

logmsg "Checkpoint: routed.dcp"
write_checkpoint -force routed.dcp
set loaded_routed 1
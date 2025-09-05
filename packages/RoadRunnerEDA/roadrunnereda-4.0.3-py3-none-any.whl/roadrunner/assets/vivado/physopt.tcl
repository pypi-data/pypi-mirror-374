if {[stepNeeded physopt.dcp $incremental] == 0} { return }
stepLoad placed.dcp $hasState

logmsg "Design: phys_opt_design"
phys_opt_design
logmsg "Checkpoint: physopt.dcp"
write_checkpoint -force physopt.dcp
set hasState 1
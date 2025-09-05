if {[stepNeeded synth.dcp $incremental] == 0} { return }

set_property target_language Verilog $prj

set args ""
#load source files with read_verilog
<% for idx,node in pairs(sources) do %>
<% for idy,fname in pairs(node.verilog) do %>
read_verilog <%-fname%>
<%end%>
<% for idy,fname in pairs(node.systemVerilog) do %>
read_verilog -sv <%-fname%>
<%end%>
<% for idy,val in pairs(node.path) do %>
lappend args -include_dirs <%-val%>
<%end%>
<% for idy,val in pairs(node.defines) do %>
lappend args -verilog_define <%-val%>
<%end%>
<%end%>

#load constraints with read_xdc
<% for idx,itm in ipairs(constraints) do %>
read_xdc <%-itm.file%>
<% if next(itm.properties) ~= nil then %>
set fx [get_files <%-itm.file%>]
<% for prop,val in pairs(itm.properties) do %>
set_property <%-prop%> <%-val%> $fx
<%end%>
<%end%>
<%end%>

#load ips with read_ip
<% for idx,fname in ipairs(ip) do %>
read_ip <%-fname%>
<%end%>

#run the synthesis
logmsg "Design: Synth"
synth_design -top <%-toplevel%> {*}$args
logmsg "Checkpoint: synth.dcp"
write_checkpoint -force -noxdef synth.dcp
logmsg "Report: synth_utilization.rpt (.pb)"
report_utilization -file synth_utilization.rpt -pb synth_utilization.pb

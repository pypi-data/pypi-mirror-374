set board <%-board%>
set part <%-part%>
set incremental <%-buildInc%>
set toplevel <%-toplevel%>

# create an in memory project
#  name: rrun
#  directory: project (probably ignored in an in-memory project)
create_project -in_memory rrun project
set prj [get_projects rrun]

# set chip and board parameters
set_property part $part $prj
if {$part != ""} {
    set_property board_part $board $prj
}

# xpm libraries
<% if #XPMLibraries > 0 then %>
set_property XPM_LIBRARIES {<%-table.concat(XPMLibraries, " ")%>} $prj
<% end %>

# logging function
proc logmsg {msg} {
    puts "##>>>>>> RRmsg: $msg"
}


proc stepNeeded {fname inc} {
    if {$inc == 0 || [file exist $fname] == 0} {
        return 1
    } else {
        logmsg "Increamental: step not needed for $fname"
        return 0
    }
}

proc stepLoad {fname loaded} {
    if {$loaded == 0} {
        logmsg "Checkpoint: load $fname"
        open_checkpoint $fname
    }
}

set hasState 0
<% for idx,stage in ipairs(stages) do %>
source <%-scripts[stage]%>
<% end %>
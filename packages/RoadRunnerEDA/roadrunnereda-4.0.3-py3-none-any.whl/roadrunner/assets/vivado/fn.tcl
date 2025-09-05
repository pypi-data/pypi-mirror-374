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
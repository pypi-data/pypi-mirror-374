package RREnv;

<% for key, val in pairs(params) do %>
localparam <%-key%> = <%-val%>
<% end %>

task RRSuccess;
    RRResult(0);
endtask

task RRFail;
    RRResult(1);
endtask

task RRResult(input int ret);
    $display("--==--==-- RoadRunner Test Result (%0d) --==--==--", ret);
endtask

endpackage
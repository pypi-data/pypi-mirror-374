<% for idx,stage in ipairs(stages) do %>
echo "running stage <%-idx%>: <%-stage%>"
source <%-scripts[stage]%>
<% end %>
echo "done"
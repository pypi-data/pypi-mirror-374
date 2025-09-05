import re
import sys

# [{
#   'pattern': r'Error:.*'
#   'occur': num || (min,max)
# }]

rules = <%-rules%>

def scanFile(fname):
    matches = [[] for _ in range(len(rules))]
    success = True
    with open(fname, "r") as fh:
        for l in fh:
            line = l.strip()
            for idx,itm in enumerate(rules):
                try:
                    pattern = itm['pattern']
                except KeyError:
                    print(f"rule {idx} does not contain 'pattern' field")
                    return False
                m = re.match(pattern, line)
                if not m:
                    continue
                matches[idx].append(line)
    #check occur rules
    for idx,itm in enumerate(rules):
        try:
            val = itm['occur']
        except KeyError:
            continue
        if isinstance(val, tuple):
            omin, omax = val
        else:
            omin, omax = val, val
        occur = len(matches[idx])
        print(f"rule #{idx}:{itm['pattern']} range:({omin},{omax}) occur:{occur}")
        if (omin is not None and occur < omin) or (omax is not None and occur > omax):
            print("rule failed!")
            success = False
    #TODO check match groups
    return success
        
for arg in sys.argv[1:]:
    print(f"Scanning file:{arg}")
    if not scanFile(arg):
        sys.exit(1)
#all good
sys.exit(0)

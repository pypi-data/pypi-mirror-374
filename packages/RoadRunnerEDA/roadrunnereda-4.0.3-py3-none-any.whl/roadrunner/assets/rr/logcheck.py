import re
import sys

REX_RESULT = r'--==--==-- RoadRunner Test Result \((\d+)\) --==--==--'

results = {}
failed = False

fname = sys.argv[1]

print(f"Scanning file:{fname}")
with open(fname) as fh:
    for line in fh:
        m = re.match(REX_RESULT, line)
        if not m:
            continue
        code = int(m.group(1))
        if code not in results:
            results[code] = 0
        if code != 0:
            failed = True
        results[code] += 1

print("Test Results:")
for code, count in results.items():
    print(f"result:{code} #:{count}")

success = None
if failed:
    success = False
    print("Failed because of non-zero test result")
elif 0 not in results:
    sucess = False
    print("Failed because of missing zero test result")
elif results[0] > 1:
    success = False
    print("Failed because of multiple zero test result")
else:
    success = True
    print("Success")

sys.exit(0 if success else 1)
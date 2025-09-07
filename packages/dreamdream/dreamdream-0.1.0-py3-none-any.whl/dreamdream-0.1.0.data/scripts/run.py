# run.py
import subprocess

p = subprocess.Popen(
    ['/flag'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)

output = p.stdout.readline().strip().split(" = ")[0]
p.stdin.write(str(eval(output)) + "\n")
p.stdin.flush()

print(p.stdout.readline().strip())
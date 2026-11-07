import json
import subprocess

res = subprocess.run(
    ["multipass.exe", "list", "--format", "json"],
    capture_output=True,
    text=True,
    check=True
)
data = json.loads(res.stdout)
for item in data["list"]:
    addresses = item["ipv4"]
    if addresses:
        ip = addresses[0]
    else:
        ip = "N/A"
    print(f"{item['name']} - {item['state']} - {ip}")

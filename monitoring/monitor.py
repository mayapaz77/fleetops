import json
import subprocess

servers = subprocess.run(
    ["multipass.exe", "list", "--format", "json"],
    capture_output=True,
    text=True,
    check=True
)
data = json.loads(servers.stdout)

for item in data["list"]:
    if item["state"] == "Running":

        # getting disk usage
        try:
            disk = subprocess.run(
                ["multipass.exe", "exec", item["name"] , "--", "df", "-Ph", "/"],
                capture_output=True,
                text=True,
                check=True
            )
            disk_output = disk.stdout.splitlines()[1].split()
            disk_usage_percent = disk_output[4]

        except subprocess.CalledProcessError:
            disk_usage_percent = "ERROR"

        # getting memory usage
        try:
            memory = subprocess.run(
                ["multipass.exe", "exec", item["name"] , "--", "free", "-b"],
                capture_output=True,
                text=True,
                check=True
            )
            memory_output = memory.stdout.splitlines()[1].split()
            total = int(memory_output[1])
            available = int(memory_output[6])
            mem_usage_percent = (total - available) / total * 100
            mem_usage_percent = f"{mem_usage_percent:.2f}%"
        except subprocess.CalledProcessError:
            mem_usage_percent = "ERROR"
        # getting ip address
        ip_addresses = item["ipv4"]
        if ip_addresses:
            ip_address = ip_addresses[0]
        else:
            ip_address = "N/A"
        print(f"""{item['name']} - {item['state']}
IP: {ip_address}
Memory: {mem_usage_percent}
Disk: {disk_usage_percent}""")
    else:
        print(f"{item['name']} - {item['state']}")


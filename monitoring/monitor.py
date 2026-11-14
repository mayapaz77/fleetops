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

        # getting cpu usage
        try:
            cpu = subprocess.run(
                ["multipass.exe", "exec", item["name"] , "--", "sh", "-c", 'top -bn2 -d 1 | grep "Cpu(s)" | tail -1'],
                capture_output=True,
                text=True,
                check=True
            )
            cpu_output = cpu.stdout.split(",")
            # taking the list of items and creating a new list with items that have the string id
            cpu_idle = list(filter(lambda item: 'id' in item, cpu_output))[0]
            cpu_idle_num = float(cpu_idle.replace(" ", "").replace("id", ""))
            cpu_usage_percent = 100 - cpu_idle_num
            cpu_usage_output = f"{cpu_usage_percent:.2f}%"

        except (subprocess.CalledProcessError, IndexError, ValueError):
            cpu_usage_output = "ERROR"

        # getting ip address
        ip_addresses = item["ipv4"]
        if ip_addresses:
            ip_address = ip_addresses[0]
        else:
            ip_address = "N/A"
        print(f"""{item['name']} - {item['state']}
IP: {ip_address}
CPU: {cpu_usage_output}
Memory: {mem_usage_percent}
Disk: {disk_usage_percent}\n""")
    else:
        print(f"{item['name']} - {item['state']}")


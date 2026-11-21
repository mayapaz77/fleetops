import json
import subprocess

# getting the list of servers
servers = subprocess.run(
    ["multipass.exe", "list", "--format", "json"],
    capture_output=True,
    text=True,
    check=True
)
data = json.loads(servers.stdout)

# def function for getting the usage level of all 3 components
def get_alert_level(usage, warning, critical):

    if usage < warning:
        return "OK"
    elif usage < critical:
        return "WARNING"
    else:
        return "CRITICAL"


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
            disk_usage_percent = float(disk_output[4].split("%")[0])
            disk_message = f"Disk: {disk_usage_percent:.0f}% - {get_alert_level(disk_usage_percent, 70, 85)}"

        except (subprocess.CalledProcessError, IndexError, ValueError):
            disk_usage_percent = "ERROR"
            disk_message = f"Disk: {disk_usage_percent}"

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
            memory_message = f"Memory: {mem_usage_percent:.2f}% - {get_alert_level(mem_usage_percent, 75, 90)}"
        except (subprocess.CalledProcessError, IndexError, ValueError, ZeroDivisionError):
            mem_usage_percent = "ERROR"
            memory_message = f"Memory: {mem_usage_percent}"

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
            cpu_message = f"CPU: {cpu_usage_percent:.2f}% - {get_alert_level(cpu_usage_percent, 80, 95)}"

        except (subprocess.CalledProcessError, IndexError, ValueError):
            cpu_usage_percent = "ERROR"
            cpu_message = f"CPU: {cpu_usage_percent}"
        # getting ip address
        ip_addresses = item["ipv4"]
        if ip_addresses:
            ip_address = ip_addresses[0]
        else:
            ip_address = "N/A"
        # printing the results
        print(f"{item['name']} - {item['state']}\nIP: {ip_address}\n{cpu_message}\n{memory_message}\n{disk_message}\n")
    else:
        print(f"{item['name']} - {item['state']}")


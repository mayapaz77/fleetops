import json
import subprocess
import sys

# getting the list of servers
try:
    servers = subprocess.run(
        ["multipass.exe", "list", "--format", "json"],
        capture_output=True,
        timeout=10,
        text=True,
        check=True
    )
    data = json.loads(servers.stdout)

except subprocess.TimeoutExpired as e:
    print(f"Multipass timed out after {e.timeout} seconds.")
    sys.exit(1)

except subprocess.CalledProcessError as e:
    print(f"Multipass failed with exit code {e.returncode}: {e.stderr}")
    sys.exit(1)

except (json.JSONDecodeError, AttributeError) as e:
    print(f"Failed to process Multipass output: {e}")
    sys.exit(1)


# def function for getting the usage level of all 3 components
def get_alert_level(usage, warning, critical):

    if usage < warning:
        return "OK"
    elif usage < critical:
        return "WARNING"
    else:
        return "CRITICAL"

results = []

try:
    list_data = data["list"]

except KeyError:
    print("ERROR: Multipass returned an unexpected JSON structure")
    sys.exit(1)

for item in list_data:
    data_dict = {}

    # making sure state key exists
    try:
        item_state = item["state"]

    except KeyError:
        item_state = "UNKNOWN"

    if item_state == "Running":

        # getting disk usage
        try:
            disk = subprocess.run(
                ["multipass.exe", "exec", item["name"] , "--", "df", "-Ph", "/"],
                capture_output=True,
                timeout=5,
                text=True,
                check=True
            )
            disk_output = disk.stdout.splitlines()[1].split()
            disk_usage_percent = float(disk_output[4].split("%")[0])


        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, IndexError, ValueError):
            disk_usage_percent = "ERROR"

        # getting memory usage
        try:
            memory = subprocess.run(
                ["multipass.exe", "exec", item["name"] , "--", "free", "-b"],
                capture_output=True,
                timeout=5,
                text=True,
                check=True
            )
            memory_output = memory.stdout.splitlines()[1].split()
            total = int(memory_output[1])
            available = int(memory_output[6])
            mem_usage_percent = (total - available) / total * 100

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, IndexError, ValueError, ZeroDivisionError):
            mem_usage_percent = "ERROR"

        # getting cpu usage
        try:
            cpu = subprocess.run(
                ["multipass.exe", "exec", item["name"] , "--", "sh", "-c", 'top -bn2 -d 1 | grep "Cpu(s)" | tail -1'],
                capture_output=True,
                timeout=5,
                text=True,
                check=True
            )
            cpu_output = cpu.stdout.split(",")
            # taking the list of items and creating a new list with items that have the string id
            cpu_idle = list(filter(lambda item: 'id' in item, cpu_output))[0]
            cpu_idle_num = float(cpu_idle.replace(" ", "").replace("id", ""))
            cpu_usage_percent = 100 - cpu_idle_num

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, IndexError, ValueError):
            cpu_usage_percent = "ERROR"

        # getting ip address
        try:
            ip_addresses = item["ipv4"]
            if ip_addresses:
                ip_address = ip_addresses[0]
            else:
                ip_address = "N/A"

        except KeyError:
            ip_address = "N/A"

        data_dict["name"] = item["name"]
        data_dict["state"] = item_state
        data_dict["disk"] = disk_usage_percent
        data_dict["memory"] = mem_usage_percent
        data_dict["cpu"] = cpu_usage_percent
        data_dict["ip"] = ip_address

        results.append(data_dict)

    # the server is not running
    else:
        data_dict["name"] = item["name"]
        data_dict["state"] = item_state
        results.append(data_dict)

# printing the results
for server_result in results:
    name = server_result['name']
    state = server_result['state']

    if state == "Running":
        ip_msg = f"IP: {server_result['ip']}"

        # set cpu message var
        if server_result['cpu'] == "ERROR":
            cpu_msg = f"CPU: {server_result['cpu']}"
        else:
            cpu_msg = f"CPU: {server_result['cpu']:.2f}% - {get_alert_level(server_result['cpu'], 80, 95)}"

        # set memory message var
        if server_result['memory'] == "ERROR":
            mem_msg = f"Memory: {server_result['memory']}"
        else:
            mem_msg = f"Memory: {server_result['memory']:.2f}% - {get_alert_level(server_result['memory'], 75, 90)}"

        # set disk message var
        if server_result['disk'] == "ERROR":
            disk_msg = f"Disk: {server_result['disk']}"
        else:
            disk_msg = f"Disk: {server_result['disk']:.0f}% - {get_alert_level(server_result['disk'], 70, 85)}"

        print(f"{name} - {state}\n{ip_msg}\n{cpu_msg}\n{mem_msg}\n{disk_msg}\n")

    else:
        print(f"{name} - {state}\n")

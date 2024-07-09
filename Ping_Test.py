import ping3
from ping3 import ping

def measure_ping():
    network_ip = input("Enter the IP address for ping test: ")
    try:
        print(f"Pinging {network_ip}...")
        latency = ping(network_ip, timeout=4)  # Added timeout for better handling
        if latency is not None:
            return f"Ping latency: {latency:.6f} seconds"
        else:
            return "Ping failed: No response"
    except Exception as e:
        return f"Ping failed: {str(e)}"

ping_result = measure_ping()
print(ping_result)

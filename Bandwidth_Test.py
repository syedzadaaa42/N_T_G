import iperf3

from N_T_G import IPERF3_AVAILABLE

def measure_bandwidth():
    if not IPERF3_AVAILABLE:
        return "iperf3 is not installed or not available"

    server = input("Enter the server IP for bandwidth test: ")
    port = int(input("Enter the port for bandwidth test: "))
    duration = int(input("Enter the duration for bandwidth test (seconds): "))

    client = iperf3.Client()
    client.duration = duration
    client.server_hostname = server
    client.port = port

    result = client.run()
    if result.error:
        return result.error
    else:
        sent = f"Sent: {result.sent_Mbps:.2f} Mbps"
        received = f"Received: {result.received_Mbps:.2f} Mbps"
        return sent, received

bandwidth_results = measure_bandwidth()
if isinstance(bandwidth_results, tuple):
    print(bandwidth_results[0])
    print(bandwidth_results[1])
else:
    print(bandwidth_results)

from scapy.all import IP, ICMP, sr1
import time

def measure_latency():
    network_ip = input("Enter the IP address for latency test: ")
    packet_count = int(input("Enter the number of packets for latency test: "))
    latencies = []

    for _ in range(packet_count):
        packet = IP(dst=network_ip) / ICMP()
        start_time = time.time()
        response = sr1(packet, timeout=1, verbose=False)
        end_time = time.time()

        if response:
            latency = end_time - start_time
            latencies.append(f"Latency: {latency:.6f} seconds")
        else:
            latencies.append("Latency: No response")

    return latencies

latency_results = measure_latency()
for result in latency_results:
    print(result)

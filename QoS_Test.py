from scapy.all import IP, TCP, Raw, sr1
import statistics
import time

def measure_qos():
    network_ip = input("Enter the IP address for QoS test: ")
    packet_count = int(input("Enter the number of packets for QoS test: "))
    traffic_type = "TCP"
    latencies = []
    packet_loss_count = 0

    for _ in range(packet_count):
        packet = IP(dst=network_ip) / TCP(dport=80) / Raw(load='X' * 64)
        start_time = time.time()
        response = sr1(packet, timeout=1, verbose=False)
        end_time = time.time()

        if response:
            latencies.append(end_time - start_time)
        else:
            packet_loss_count += 1

    if latencies:
        average_latency = sum(latencies) / len(latencies)
        jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
    else:
        average_latency = jitter = 0.0

    packet_loss_percentage = (packet_loss_count / packet_count) * 100

    return (f"Average Latency: {average_latency:.6f} seconds",
            f"Jitter: {jitter:.6f} seconds",
            f"Packet Loss: {packet_loss_percentage:.2f}%")

qos_results = measure_qos()
for result in qos_results:
    print(result)

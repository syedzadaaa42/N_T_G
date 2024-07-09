from scapy.all import IP, UDP, Raw, send
import time

def measure_throughput():
    network_ip = input("Enter the IP address for throughput test: ")
    packet_size = int(input("Enter the packet size for throughput test (bytes): "))
    duration = int(input("Enter the duration for throughput test (seconds): "))
    packet = IP(dst=network_ip) / UDP(dport=80) / Raw(load='X' * (packet_size - 20 - 8))
    start_time = time.time()
    packet_count = 0

    while time.time() - start_time < duration:
        send(packet, verbose=False)
        packet_count += 1

    end_time = time.time()
    elapsed_time = end_time - start_time
    throughput = (packet_size * packet_count * 8) / elapsed_time  # bits per second
    throughput_mbps = throughput / 1_000_000  # Mbps
    return f"Throughput: {throughput_mbps:.2f} Mbps"

throughput_result = measure_throughput()
print(throughput_result)

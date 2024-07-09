from scapy.all import IP, TCP, Raw, send
import time

def perform_load_test():
    network_ip = input("Enter the IP address for load test: ")
    frame_length = int(input("Enter the frame length for load test: "))
    duration = int(input("Enter the duration for load test (seconds): "))
    payload = 'X' * (frame_length - 20 - 20)
    packet = IP(dst=network_ip) / TCP(dport=80) / Raw(load=payload)
    start_time = time.time()
    packet_count = 0

    while time.time() - start_time < duration:
        send(packet, verbose=False)
        packet_count += 1

    end_time = time.time()
    elapsed_time = end_time - start_time
    load_throughput = (frame_length * packet_count * 8) / elapsed_time  # bits per second
    load_throughput_mbps = load_throughput / 1_000_000  # Mbps
    return f"Load Test Throughput: {load_throughput_mbps:.2f} Mbps"

load_test_result = perform_load_test()
print(load_test_result)

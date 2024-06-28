from scapy.all import IP, ICMP, sr1, send
import iperf3
import speedtest
import ping3
import time

class NetworkTester:
    def __init__(self, network_ip, packet_count):
        self.network_ip = network_ip
        self.packet_count = packet_count

    def measure_speed(self):
        st = speedtest.Speedtest()
        st.download()
        st.upload()
        results = st.results.dict()
        print(f"Download speed: {results['download'] / 1_000_000:.2f} Mbps")
        print(f"Upload speed: {results['upload'] / 1_000_000:.2f} Mbps")
        return results

    def measure_latency(self):
        packet = IP(dst=self.network_ip) / ICMP()
        start_time = time.time()
        response = sr1(packet, timeout=1, verbose=False)
        end_time = time.time()

        if response:
            latency = end_time - start_time
            print(f"Latency: {latency} seconds")
            return latency
        else:
            print("No response")
            return None

    def measure_throughput(self, packet_size=1024, duration=10):
        packet = IP(dst=self.network_ip) / UDP(dport=12345) / (b'X' * packet_size)
        start_time = time.time()
        packet_count = 0

        while time.time() - start_time < duration:
            send(packet, verbose=False)
            packet_count += 1

        end_time = time.time()
        elapsed_time = end_time - start_time
        throughput = (packet_size * packet_count * 8) / elapsed_time  # bits per second
        throughput_mbps = throughput / 1_000_000  # Mbps
        print(f"Throughput: {throughput_mbps:.2f} Mbps")
        return throughput_mbps

    def measure_bandwidth(self, server='iperf-server.example.com', port=5201, duration=10):
        client = iperf3.Client()
        client.duration = duration
        client.server_hostname = server
        client.port = port

        result = client.run()
        if result.error:
            print(result.error)
            return None
        else:
            print(f"Sent: {result.sent_Mbps} Mbps")
            print(f"Received: {result.received_Mbps} Mbps")
            return result

    def measure_ping(self):
        latency = ping3.ping(self.network_ip)
        print(f"Ping latency: {latency} seconds")
        return latency

    def run_all_tests(self):
        print("Running Network Tests...\n")

        print("Speed Test:")
        self.measure_speed()

        print("\nLatency Test:")
        self.measure_latency()

        print("\nThroughput Test:")
        self.measure_throughput(duration=self.packet_count)

        print("\nBandwidth Test:")
        self.measure_bandwidth(server=self.network_ip)

        print("\nPing Test:")
        self.measure_ping()


def main():
    # Get user input
    network_ip = input("Enter the IP address of the network to test: ")
    packet_count = int(input("Enter the number of packets to send: "))

    # Create a NetworkTester instance
    tester = NetworkTester(network_ip, packet_count)

    # Run all tests
    tester.run_all_tests()


if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk
from scapy.all import IP, ICMP, sr1, send, UDP
import iperf3
import speedtest
import ping3
import time
import threading
import statistics

class NetworkTester:
    def __init__(self, network_ip, packet_count):
        self.network_ip = network_ip
        self.packet_count = packet_count

    def measure_speed(self):
        st = speedtest.Speedtest()
        st.download()
        st.upload()
        results = st.results.dict()
        download_speed = f"Download speed: {results['download'] / 1_000_000:.2f} Mbps"
        upload_speed = f"Upload speed: {results['upload'] / 1_000_000:.2f} Mbps"
        return download_speed, upload_speed

    def measure_latency(self):
        packet = IP(dst=self.network_ip) / ICMP()
        start_time = time.time()
        response = sr1(packet, timeout=1, verbose=False)
        end_time = time.time()

        if response:
            latency = end_time - start_time
            return f"Latency: {latency:.6f} seconds"
        else:
            return "No response"

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
        return f"Throughput: {throughput_mbps:.2f} Mbps"

    def measure_bandwidth(self, server='iperf-server.example.com', port=5201, duration=10):
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

    def measure_ping(self):
        latency = ping3.ping(self.network_ip)
        return f"Ping latency: {latency:.6f} seconds"

    def measure_qos(self):
        latencies = []
        packet_loss_count = 0

        for _ in range(self.packet_count):
            packet = IP(dst=self.network_ip) / ICMP()
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

        packet_loss_percentage = (packet_loss_count / self.packet_count) * 100

        return (f"Average Latency: {average_latency:.6f} seconds",
                f"Jitter: {jitter:.6f} seconds",
                f"Packet Loss: {packet_loss_percentage:.2f}%")

    def run_all_tests(self):
        results = []
        
        results.append("Running Network Tests...\n")

        results.append("Speed Test:")
        download_speed, upload_speed = self.measure_speed()
        results.append(download_speed)
        results.append(upload_speed)

        results.append("\nLatency Test:")
        results.append(self.measure_latency())

        results.append("\nThroughput Test:")
        results.append(self.measure_throughput(duration=self.packet_count))

        results.append("\nBandwidth Test:")
        bandwidth_results = self.measure_bandwidth(server=self.network_ip)
        if isinstance(bandwidth_results, tuple):
            results.extend(bandwidth_results)
        else:
            results.append(bandwidth_results)

        results.append("\nPing Test:")
        results.append(self.measure_ping())

        results.append("\nQoS Metrics:")
        qos_results = self.measure_qos()
        results.extend(qos_results)
        
        return "\n".join(results)

class NetworkTesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Tester")

        self.network_ip_label = ttk.Label(root, text="Enter the IP address of the network to test:")
        self.network_ip_label.grid(row=0, column=0, padx=10, pady=10)
        self.network_ip_entry = ttk.Entry(root)
        self.network_ip_entry.grid(row=0, column=1, padx=10, pady=10)

        self.packet_count_label = ttk.Label(root, text="Enter the number of packets to send:")
        self.packet_count_label.grid(row=1, column=0, padx=10, pady=10)
        self.packet_count_entry = ttk.Entry(root)
        self.packet_count_entry.grid(row=1, column=1, padx=10, pady=10)

        self.start_button = ttk.Button(root, text="Start Tests", command=self.start_tests)
        self.start_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.results_text = tk.Text(root, height=30, width=80)
        self.results_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def start_tests(self):
        network_ip = self.network_ip_entry.get()
        packet_count = int(self.packet_count_entry.get())
        tester = NetworkTester(network_ip, packet_count)
        self.results_text.delete(1.0, tk.END)
        
        # Run tests in a separate thread to keep the GUI responsive
        threading.Thread(target=self.run_tests, args=(tester,)).start()

    def run_tests(self, tester):
        results = tester.run_all_tests()
        self.results_text.insert(tk.END, results)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkTesterGUI(root)
    root.mainloop()

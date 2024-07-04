import warnings
warnings.filterwarnings("ignore", message="Wireshark is installed, but cannot read manuf")

import tkinter as tk
from tkinter import ttk
from scapy.all import IP, ICMP, sr1, send, UDP, TCP, Raw
import speedtest
import ping3
import time
import threading
import statistics
import subprocess
import random
import struct

# Attempt to import iperf3, handle if not available
try:
    import iperf3
    IPERF3_AVAILABLE = True
except ImportError:
    IPERF3_AVAILABLE = False

# Map traffic types to their corresponding port numbers
TRAFFIC_TYPE_PORT_MAP = {
    "TCP": 80,
    "FTP": 21,
    "HTTP": 80,
    "SMTP": 25,
    "POP3": 110,
    "SSH": 22,
    "NTP": 123,
    "Telnet": 23,
    "EIGRP": 88,  # Example port for EIGRP
    "OSPF": 89,   # Example port for OSPF
    "RTP": 5004,  # Standard RTP port
}

class NetworkTester:
    def __init__(self, network_ip, packet_count, traffic_type, frame_length, update_progress):
        self.network_ip = network_ip
        self.packet_count = packet_count
        self.traffic_type = traffic_type
        self.frame_length = frame_length
        self.update_progress = update_progress
        self.total_tests = 8  # Number of tests to perform, including port scan and load test

    def create_packet(self):
        payload = 'X' * (self.frame_length - 20 - 20)  # Adjust for IP and TCP/UDP headers

        if self.traffic_type == "RTP":
            return self.create_rtp_packet()

        elif self.traffic_type == "TCP":
            return IP(dst=self.network_ip) / TCP(dport=TRAFFIC_TYPE_PORT_MAP["TCP"]) / Raw(load=payload)
        elif self.traffic_type == "FTP":
            return IP(dst=self.network_ip) / TCP(dport=TRAFFIC_TYPE_PORT_MAP["FTP"]) / Raw(load=payload)
        elif self.traffic_type == "HTTP":
            return IP(dst=self.network_ip) / TCP(dport=TRAFFIC_TYPE_PORT_MAP["HTTP"]) / Raw(load=payload)
        elif self.traffic_type == "SMTP":
            return IP(dst=self.network_ip) / TCP(dport=TRAFFIC_TYPE_PORT_MAP["SMTP"]) / Raw(load=payload)
        elif self.traffic_type == "POP3":
            return IP(dst=self.network_ip) / TCP(dport=TRAFFIC_TYPE_PORT_MAP["POP3"]) / Raw(load=payload)
        elif self.traffic_type == "SSH":
            return IP(dst=self.network_ip) / TCP(dport=TRAFFIC_TYPE_PORT_MAP["SSH"]) / Raw(load=payload)
        elif self.traffic_type == "NTP":
            return IP(dst=self.network_ip) / UDP(dport=TRAFFIC_TYPE_PORT_MAP["NTP"]) / Raw(load=payload)
        elif self.traffic_type == "Telnet":
            return IP(dst=self.network_ip) / TCP(dport=TRAFFIC_TYPE_PORT_MAP["Telnet"]) / Raw(load=payload)
        elif self.traffic_type == "EIGRP":
            # EIGRP is not supported, use ICMP as a placeholder
            return IP(dst=self.network_ip) / ICMP() / Raw(load=payload)
        elif self.traffic_type == "OSPF":
            # OSPF is not supported, use ICMP as a placeholder
            return IP(dst=self.network_ip) / ICMP() / Raw(load=payload)
        else:
            return IP(dst=self.network_ip) / ICMP() / Raw(load=payload)

    def create_rtp_packet(self):
        # Create a dummy RTP packet
        rtp_version = 2
        rtp_padding = 0
        rtp_extension = 0
        rtp_csrc_count = 0
        rtp_marker = 0
        rtp_payload_type = 96  # Dynamic payload type for video/audio
        rtp_sequence_number = random.randint(0, 65535)
        rtp_timestamp = random.randint(0, 4294967295)
        rtp_ssrc = random.randint(0, 4294967295)
        rtp_payload = 'A' * (self.frame_length - 12)  # RTP header is 12 bytes

        rtp_header = (
            (rtp_version << 6) | (rtp_padding << 5) | (rtp_extension << 4) | rtp_csrc_count,
            (rtp_marker << 7) | rtp_payload_type,
            rtp_sequence_number,
            rtp_timestamp,
            rtp_ssrc
        )

        rtp_packet = struct.pack('!BBHII', *rtp_header) + rtp_payload.encode('utf-8')
        return IP(dst=self.network_ip) / UDP(dport=TRAFFIC_TYPE_PORT_MAP["RTP"]) / Raw(load=rtp_packet)

    def measure_speed(self):
        self.update_progress("Running Speed Test...", 0, self.total_tests)
        try:
            st = speedtest.Speedtest()
            st.download()
            st.upload()
            results = st.results.dict()
            download_speed = f"Download speed: {results['download'] / 1_000_000:.2f} Mbps"
            upload_speed = f"Upload speed: {results['upload'] / 1_000_000:.2f} Mbps"
        except Exception as e:
            download_speed = "Speed Test Failed"
            upload_speed = str(e)
        self.update_progress("Speed Test Completed", 1, self.total_tests)
        return download_speed, upload_speed

    def measure_latency(self):
        self.update_progress("Running Latency Test...", 1, self.total_tests)
        packet = self.create_packet()
        start_time = time.time()
        response = sr1(packet, timeout=1, verbose=False)
        end_time = time.time()

        if response:
            latency = end_time - start_time
            self.update_progress("Latency Test Completed", 2, self.total_tests)
            return f"Latency: {latency:.6f} seconds"
        else:
            self.update_progress("Latency Test Failed", 2, self.total_tests)
            return "No response"

    def measure_throughput(self, packet_size=1024, duration=10):
        self.update_progress("Running Throughput Test...", 2, self.total_tests)
        packet = self.create_packet()
        start_time = time.time()
        packet_count = 0

        while time.time() - start_time < duration:
            send(packet, verbose=False)
            packet_count += 1

        end_time = time.time()
        elapsed_time = end_time - start_time
        throughput = (packet_size * packet_count * 8) / elapsed_time  # bits per second
        throughput_mbps = throughput / 1_000_000  # Mbps
        self.update_progress("Throughput Test Completed", 3, self.total_tests)
        return f"Throughput: {throughput_mbps:.2f} Mbps"

    def measure_bandwidth(self, server='iperf-server.example.com', port=5201, duration=10):
        self.update_progress("Running Bandwidth Test...", 3, self.total_tests)
        if not IPERF3_AVAILABLE:
            self.update_progress("Bandwidth Test Failed: iperf3 not available", 4, self.total_tests)
            return "iperf3 is not installed or not available"

        # Check if iperf3 executable is available
        try:
            result = subprocess.run(["iperf3", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())  # This will print the version info to the console for verification
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.update_progress("Bandwidth Test Failed: iperf3 executable not found", 4, self.total_tests)
            return "iperf3 executable not found or not accessible"

        client = iperf3.Client()
        client.duration = duration
        client.server_hostname = server
        client.port = port

        result = client.run()
        if result.error:
            self.update_progress(f"Bandwidth Test Failed: {result.error}", 4, self.total_tests)
            return result.error
        else:
            sent = f"Sent: {result.sent_Mbps:.2f} Mbps"
            received = f"Received: {result.received_Mbps:.2f} Mbps"
            self.update_progress("Bandwidth Test Completed", 4, self.total_tests)
            return sent, received

    def measure_ping(self):
        self.update_progress("Running Ping Test...", 4, self.total_tests)
        latency = ping3.ping(self.network_ip)
        self.update_progress("Ping Test Completed", 5, self.total_tests)
        return f"Ping latency: {latency:.6f} seconds"

    def measure_qos(self):
        self.update_progress("Running QoS Metrics...", 5, self.total_tests)
        latencies = []
        packet_loss_count = 0

        for _ in range(self.packet_count):
            packet = self.create_packet()
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

        self.update_progress("QoS Metrics Completed", 6, self.total_tests)
        return (f"Average Latency: {average_latency:.6f} seconds",
                f"Jitter: {jitter:.6f} seconds",
                f"Packet Loss: {packet_loss_percentage:.2f}%")

    def perform_port_scan(self):
        self.update_progress("Performing Port Scan...", 6, self.total_tests)
        port = TRAFFIC_TYPE_PORT_MAP.get(self.traffic_type, None)
        open_ports = []
        if port:
            packet = IP(dst=self.network_ip) / TCP(dport=port, flags="S")
            response = sr1(packet, timeout=0.5, verbose=False)
            if response and response.haslayer(TCP) and response.getlayer(TCP).flags == 0x12:
                open_ports.append(port)
                send(IP(dst=self.network_ip) / TCP(dport=port, flags="R"), verbose=False)
        self.update_progress("Port Scan Completed", 7, self.total_tests)
        return open_ports

    def perform_load_test(self, duration=30):
        self.update_progress("Running Load Test...", 7, self.total_tests)
        packet = self.create_packet()
        start_time = time.time()
        packet_count = 0

        while time.time() - start_time < duration:
            send(packet, verbose=False)
            packet_count += 1

        end_time = time.time()
        elapsed_time = end_time - start_time
        load_throughput = (self.frame_length * packet_count * 8) / elapsed_time  # bits per second
        load_throughput_mbps = load_throughput / 1_000_000  # Mbps
        self.update_progress("Load Test Completed", 8, self.total_tests)
        return f"Load Test Throughput: {load_throughput_mbps:.2f} Mbps"

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

        results.append("\nPort Scan:")
        open_ports = self.perform_port_scan()
        results.append(f"Open port: {open_ports[0]}" if open_ports else "No open ports found.")

        results.append("\nLoad Test:")
        results.append(self.perform_load_test())

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

        self.traffic_label = ttk.Label(root, text="Select Traffic Type:")
        self.traffic_label.grid(row=2, column=0, padx=10, pady=10)
        self.traffic_types = ["TCP", "FTP", "HTTP", "SMTP", "POP3", "SSH", "NTP", "Telnet", "EIGRP", "OSPF", "RTP"]
        self.traffic_type = ttk.Combobox(root, values=self.traffic_types)
        self.traffic_type.grid(row=2, column=1, padx=10, pady=10)
        self.traffic_type.set(self.traffic_types[0])  # Default to the first traffic type

        self.frame_label = ttk.Label(root, text="Select Frame Length:")
        self.frame_label.grid(row=3, column=0, padx=10, pady=10)
        self.frame_lengths = [64, 128, 256, 512, 1024, 1500]
        self.frame_length = ttk.Combobox(root, values=self.frame_lengths)
        self.frame_length.grid(row=3, column=1, padx=10, pady=10)
        self.frame_length.set(self.frame_lengths[0])  # Default to the first frame length

        self.start_button = ttk.Button(root, text="Start Tests", command=self.start_tests)
        self.start_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.grid(row=4, column=2, padx=10, pady=10)

        self.results_text = tk.Text(root, height=30, width=80)
        self.results_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        self.progress_label = ttk.Label(root, text="")
        self.progress_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

        self.tester = None
        self.start_time = None

    def start_tests(self):
        network_ip = self.network_ip_entry.get()
        packet_count = int(self.packet_count_entry.get())
        traffic_type = self.traffic_type.get()
        frame_length = int(self.frame_length.get())
        self.tester = NetworkTester(network_ip, packet_count, traffic_type, frame_length, self.update_progress)
        self.results_text.delete(1.0, tk.END)
        self.progress["value"] = 0
        self.progress_label.config(text="Starting tests...")
        self.start_time = time.time()

        # Run tests in a separate thread to keep the GUI responsive
        threading.Thread(target=self.run_tests, args=(self.tester,)).start()

    def run_tests(self, tester):
        results = tester.run_all_tests()
        self.results_text.insert(tk.END, results)
        self.progress_label.config(text="Tests completed.")
        self.progress["value"] = 100

    def update_progress(self, message, current_step, total_steps):
        progress_percentage = (current_step / total_steps) * 100
        elapsed_time = time.time() - self.start_time
        estimated_total_time = elapsed_time / current_step * total_steps if current_step > 0 else 0
        remaining_time = estimated_total_time - elapsed_time
        remaining_time_formatted = time.strftime("%H:%M:%S", time.gmtime(remaining_time))
        self.progress_label.config(
            text=f"{message} - {progress_percentage:.2f}% complete - Time remaining: {remaining_time_formatted}")
        self.progress["value"] = progress_percentage


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkTesterGUI(root)
    root.mainloop()

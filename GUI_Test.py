import tkinter as tk
from tkinter import ttk
import time
import threading

class NetworkTesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Tester")

        self.network_ip_label = ttk.Label(root, text="Enter the IP address of the network to test:")
        self.network_ip_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.network_ip_entry = ttk.Entry(root)
        self.network_ip_entry.grid(row=0, column=1, padx=10, pady=10)

        self.packet_count_label = ttk.Label(root, text="Enter the number of packets to send:")
        self.packet_count_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.packet_count_entry = ttk.Entry(root)
        self.packet_count_entry.grid(row=1, column=1, padx=10, pady=10)

        self.traffic_label = ttk.Label(root, text="Select Traffic Type(s):")
        self.traffic_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.traffic_type_vars = {}
        self.traffic_types = ["TCP", "FTP", "HTTP", "SMTP", "POP3", "SSH", "NTP", "Telnet", "EIGRP", "OSPF", "RTP"]
        for i, traffic_type in enumerate(self.traffic_types):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(root, text=traffic_type, variable=var)
            chk.grid(row=2+i//3, column=1+i%3, padx=5, pady=5, sticky=tk.W)
            self.traffic_type_vars[traffic_type] = var

        self.frame_label = ttk.Label(root, text="Select Frame Length:")
        self.frame_label.grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)
        self.frame_lengths = [64, 128, 256, 512, 1024, 1500]
        self.frame_length = ttk.Combobox(root, values=self.frame_lengths)
        self.frame_length.grid(row=6, column=1, padx=10, pady=10)
        self.frame_length.set(self.frame_lengths[0])  # Default to the first frame length

        self.start_button = ttk.Button(root, text="Generate Traffic", command=self.start_tests)
        self.start_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.grid(row=7, column=2, padx=10, pady=10)

        self.results_text = tk.Text(root, height=20, width=80)
        self.results_text.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

        self.progress_label = ttk.Label(root, text="")
        self.progress_label.grid(row=9, column=0, columnspan=3, padx=10, pady=10)

        self.tester = None
        self.start_time = None

    def start_tests(self):
        network_ip = self.network_ip_entry.get()
        packet_count = int(self.packet_count_entry.get())
        traffic_types = [traffic_type for traffic_type, var in self.traffic_type_vars.items() if var.get()]
        frame_length = int(self.frame_length.get())
        # Simulate a tester object for GUI testing
        self.tester = DummyTester(network_ip, packet_count, traffic_types, frame_length, self.update_progress)
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

class DummyTester:
    def __init__(self, network_ip, packet_count, traffic_types, frame_length, update_progress):
        self.network_ip = network_ip
        self.packet_count = packet_count
        self.traffic_types = traffic_types
        self.frame_length = frame_length
        self.update_progress = update_progress
        self.total_tests = 8

    def run_all_tests(self):
        results = []
        for i in range(self.total_tests):
            time.sleep(1)
            self.update_progress(f"Running test {i+1}", i+1, self.total_tests)
            results.append(f"Result of test {i+1}")
        return "\n".join(results)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkTesterGUI(root)
    root.mainloop()

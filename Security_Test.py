from scapy.all import IP, TCP, sr1, send

TRAFFIC_TYPE_PORT_MAP = {
    "TCP": 80,
    "FTP": 21,
    "HTTP": 80,
    "SMTP": 25,
    "POP3": 110,
    "SSH": 22,
    "NTP": 123,
    "Telnet": 23,
    "EIGRP": 88,  # Example port number, you may need to correct this
    "OSPF": 89,   # Example port number, you may need to correct this
    "RTP": 5004   # Example port number, you may need to correct this
}

def perform_port_scan():
    network_ip = input("Enter the IP address for port scan: ")
    traffic_types = ["TCP", "FTP", "HTTP", "SMTP", "POP3", "SSH", "NTP", "Telnet", "EIGRP", "OSPF", "RTP"]
    open_ports = []

    for traffic_type in traffic_types:
        port = TRAFFIC_TYPE_PORT_MAP.get(traffic_type, None)
        if port:
            packet = IP(dst=network_ip) / TCP(dport=port, flags="S")
            response = sr1(packet, timeout=0.5, verbose=False)
            if response and response.haslayer(TCP) and response.getlayer(TCP).flags == 0x12:
                open_ports.append((traffic_type, port))
                send(IP(dst=network_ip) / TCP(dport=port, flags="R"), verbose=False)
    return open_ports

open_ports = perform_port_scan()
for port in open_ports:
    print(f"{port[0]}: Open port: {port[1]}")
if not open_ports:
    print("No open ports found.")

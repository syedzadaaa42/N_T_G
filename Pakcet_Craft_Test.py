from scapy.all import IP, TCP, Raw, send

def create_packet():
    network_ip = input("Enter the IP address for packet manipulation test: ")
    frame_length = int(input("Enter the frame length for packet manipulation test: "))
    payload = 'X' * (frame_length - 20 - 20)  # Adjust for IP and TCP/UDP headers
    packet = IP(dst=network_ip) / TCP(dport=80) / Raw(load=payload)
    send(packet, verbose=False)
    return f"Packet crafted and sent to {network_ip} with frame length {frame_length}"

packet_manipulation_result = create_packet()
print(packet_manipulation_result)

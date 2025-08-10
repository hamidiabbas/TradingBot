"""
Windows Performance Monitor
==========================
"""

import psutil
import time
import threading
from datetime import datetime

class WindowsPerformanceMonitor:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("📊 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("📊 Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # GPU metrics (if available)
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                gpu_info = f"GPU: {gpus[0].load*100:.1f}%" if gpus else "GPU: N/A"
            except:
                gpu_info = "GPU: N/A"
            
            print(f"⚡ [{datetime.now().strftime('%H:%M:%S')}] "
                  f"CPU: {cpu_percent:.1f}% | "
                  f"RAM: {memory.percent:.1f}% | "
                  f"Disk: {disk.percent:.1f}% | "
                  f"{gpu_info}")
            
            time.sleep(30)  # Update every 30 seconds

# Usage example
if __name__ == "__main__":
    monitor = WindowsPerformanceMonitor()
    monitor.start_monitoring()
    
    try:
        time.sleep(300)  # Monitor for 5 minutes
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop_monitoring()

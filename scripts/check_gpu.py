"""
GPU Availability Checker for Windows
===================================
"""

def check_gpu_setup():
    print("🎮 === GPU AVAILABILITY CHECK ===")
    
    # Check NVIDIA GPU
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            for i, gpu in enumerate(gpus):
                print(f"🎮 GPU {i}: {gpu.name}")
                print(f"   Memory: {gpu.memoryTotal}MB total, {gpu.memoryFree}MB free")
                print(f"   Load: {gpu.load*100:.1f}%")
        else:
            print("⚠️ No NVIDIA GPUs found")
    except ImportError:
        print("⚠️ GPUtil not installed")
    
    # Check TensorFlow GPU
    try:
        import tensorflow as tf
        print(f"🧠 TensorFlow version: {tf.__version__}")
        
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"✅ TensorFlow can see {len(gpus)} GPU(s)")
            for gpu in gpus:
                print(f"   {gpu}")
        else:
            print("⚠️ TensorFlow cannot see GPU")
    except ImportError:
        print("❌ TensorFlow not installed")
    
    # Check PyTorch GPU (optional)
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ PyTorch CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️ PyTorch CUDA not available")
    except ImportError:
        print("⚠️ PyTorch not installed")

if __name__ == "__main__":
    check_gpu_setup()

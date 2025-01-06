import torch
def get_device(force_cpu=False):
    if force_cpu:
        return torch.device("cpu")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")

# 使用 MPS (GPU)
device = get_device()
print(f"目前使用設備: {device}")

# 強制使用 CPU
device = get_device(force_cpu=True)
print(f"切換到: {device}")
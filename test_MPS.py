import torch
print("MPS 是否可用:", torch.backends.mps.is_available())
print("MPS 是否已建置:", torch.backends.mps.is_built())

#MPS=Metal Performance Shaders(金屬性能著色器)
# MPS 是否可用: True
# MPS 是否已建置: True


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")



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
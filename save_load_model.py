import torch

# 保存模型和詞彙表大小
def save_model(model, vocab_size, file_path):
    torch.save({
        'model_state_dict': model.state_dict(),
        'vocab_size': vocab_size
    }, file_path)

# 加载模型和詞彙表大小
def load_model(model, file_path):
    checkpoint = torch.load(file_path, weights_only=True)
    model.load_state_dict(checkpoint['model_state_dict'])
    return checkpoint['vocab_size']

# 示例
if __name__ == "__main__":
    from model import LanguageModel

    vocab_size = 1000  # 词汇表大小
    embed_size = 128  # 嵌入维度
    hidden_size = 256  # 隐藏层维度
    model = LanguageModel(vocab_size, embed_size, hidden_size)

    save_model(model, vocab_size, "ntnuchatAI/language_model.pth")
    loaded_vocab_size = load_model(model, "ntnuchatAI/language_model.pth")
    print(f"Loaded vocab size: {loaded_vocab_size}")

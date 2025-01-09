import torch
import torch.nn as nn

class LanguageModel(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super(LanguageModel, self).__init__()
        self.vocab_size = vocab_size  # 添加這行來追踪詞彙表大小
        self.embed_size = embed_size
        self.hidden_size = hidden_size
        
        # 確保詞彙表大小至少為1000
        self.vocab_size = max(1000, vocab_size)
        
        self.embedding = nn.Embedding(self.vocab_size, embed_size)
        self.rnn = nn.LSTM(embed_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, self.vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        out, _ = self.rnn(x)
        out = self.fc(out[:, -1, :])
        return out
    
    def get_config(self):
        return {
            'vocab_size': self.vocab_size,
            'embed_size': self.embed_size,
            'hidden_size': self.hidden_size
        }

# 測試代碼
if __name__ == "__main__":
    vocab_size = 1000  # 確保詞彙表大小為1000
    embed_size = 128
    hidden_size = 256
    model = LanguageModel(vocab_size, embed_size, hidden_size)
    print(model)
    print(f"Model configuration: {model.get_config()}")
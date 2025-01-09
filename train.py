import torch
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from model import LanguageModel
import torch.nn as nn

#06_train:訓練模型
# 数据加载
def load_data(inputs, targets, batch_size):
    dataset = TensorDataset(torch.tensor(inputs, dtype=torch.long), torch.tensor(targets, dtype=torch.long))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    return loader

# 训练模型
def train_model(model, loader, criterion, optimizer, epochs):
    for epoch in range(epochs):
        for x_batch, y_batch in loader:
            optimizer.zero_grad()
            outputs = model(x_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")

# 示例
if __name__ == "__main__":
    from data_preparation import create_sequences
    from tokenization import build_vocab, text_to_tokens
    from data_cleaning import clean_text
    from data_extraction import extract_pdf_text, extract_word_text

    pdf_text = extract_pdf_text("/Users/sma01/Downloads/testdata.pdf")
    word_text = extract_word_text("/Users/sma01/Downloads/testdata.docx")
    all_text = pdf_text + word_text
    cleaned_text = clean_text(all_text)
    vocab = build_vocab(cleaned_text)
    tokens = text_to_tokens(cleaned_text, vocab)
    seq_length = 10  # 序列长度
    inputs, targets = create_sequences(tokens, seq_length)

    batch_size = 32
    loader = load_data(inputs, targets, batch_size)

    vocab_size = len(vocab) + 1  # 词汇表大小
    embed_size = 128  # 嵌入维度
    hidden_size = 256  # 隐藏层维度
    model = LanguageModel(vocab_size, embed_size, hidden_size)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    epochs = 5
    train_model(model, loader, criterion, optimizer, epochs)

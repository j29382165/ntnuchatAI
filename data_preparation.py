import numpy as np

#04_data_preparation：將 Token 序列切分為輸入和目標
# 序列化数据
def create_sequences(tokens, seq_length):
    inputs, targets = [], []
    for i in range(len(tokens) - seq_length):
        inputs.append(tokens[i:i + seq_length])
        targets.append(tokens[i + seq_length])
    return np.array(inputs), np.array(targets)

# 示例
if __name__ == "__main__":
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
    print(inputs.shape, targets.shape)

from collections import defaultdict

#03_tokenization:將文本轉換為 Token
# 构建词汇表
def build_vocab(text):
    words = text.split()
    vocab = {word: idx for idx, word in enumerate(set(words), start=1)}
    return vocab

# 转换文本为 Token
def text_to_tokens(text, vocab):
    tokens = [vocab[word] for word in text.split() if word in vocab]
    return tokens

# 示例
if __name__ == "__main__":
    from data_cleaning import clean_text
    from data_extraction import extract_pdf_text, extract_word_text

    pdf_text = extract_pdf_text("/Users/sma01/Downloads/testdata.pdf")
    word_text = extract_word_text("/Users/sma01/Downloads/testdata.docx")
    all_text = pdf_text + word_text
    cleaned_text = clean_text(all_text)
    vocab = build_vocab(cleaned_text)
    tokens = text_to_tokens(cleaned_text, vocab)
    print(tokens[:100])  # 查看前 100 个 Token

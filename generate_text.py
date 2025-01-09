import torch
from typing import Dict, List

def generate_text(model: torch.nn.Module, 
                 start_text: str, 
                 vocab: Dict[str, int], 
                 inv_vocab: Dict[int, str] = None,
                 max_length: int = 50,
                 seq_length: int = 10) -> str:
    """
    生成文本的函數
    
    Args:
        model: 訓練好的語言模型
        start_text: 起始文本
        vocab: 詞彙表 (word -> id)
        inv_vocab: 反向詞彙表 (id -> word)
        max_length: 生成文本的最大長度
        seq_length: 序列長度
    """
    # 創建反向詞彙表（如果沒有提供）
    if inv_vocab is None:
        inv_vocab = {v: k for k, v in vocab.items()}
    
    model.eval()
    words = start_text.split()
    
    # 處理輸入序列
    input_ids = []
    for word in words:
        # 如果詞不在詞彙表中，使用UNK或第一個詞
        word_id = vocab.get(word, 0)
        # 確保id不超過模型的詞彙表大小
        word_id = min(word_id, model.vocab_size - 1)
        input_ids.append(word_id)
    
    input_seq = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0)
    
    # 生成文本
    with torch.no_grad():
        for _ in range(max_length):
            # 確保輸入序列不超過seq_length
            if input_seq.size(1) > seq_length:
                input_seq = input_seq[:, -seq_length:]
                
            try:
                output = model(input_seq)
                next_word_id = torch.argmax(output, dim=1).item()
                
                # 確保生成的id有對應的詞
                if next_word_id in inv_vocab:
                    words.append(inv_vocab[next_word_id])
                else:
                    # 如果id超出範圍，使用一個替代詞
                    words.append("<UNK>")
                
                # 更新輸入序列
                input_ids = [vocab.get(w, 0) for w in words[-seq_length:]]
                input_seq = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0)
                
            except Exception as e:
                print(f"Error during text generation: {e}")
                break
    
    return " ".join(words)

# 主程序
if __name__ == "__main__":
    from model import LanguageModel
    from save_load_model import load_model
    from tokenization import build_vocab
    from data_cleaning import clean_text
    from data_extraction import extract_pdf_text, extract_word_text

    try:
        # 讀取數據
        pdf_text = extract_pdf_text("/Users/sma01/Downloads/testdata.pdf")
        word_text = extract_word_text("/Users/sma01/Downloads/testdata.docx")
        all_text = pdf_text + word_text
        cleaned_text = clean_text(all_text)
        
        # 構建詞彙表
        vocab = build_vocab(cleaned_text)
        vocab_size = max(1000, len(vocab) + 1)  # 確保詞彙表大小至少為1000
        
        # 創建反向詞彙表
        inv_vocab = {v: k for k, v in vocab.items()}
        
        # 初始化模型
        embed_size = 128
        hidden_size = 256
        model = LanguageModel(vocab_size, embed_size, hidden_size)
        
        # 加載模型
        loaded_vocab_size = load_model(model, "ntnuchatAI/language_model.pth")
        print(f"Loaded model vocab size: {loaded_vocab_size}")
        print(f"Current vocab size: {len(vocab)}")
        
        # 生成文本
        start_text = "中文名"
        generated_text = generate_text(
            model=model,
            start_text=start_text,
            vocab=vocab,
            inv_vocab=inv_vocab,
            max_length=50,
            seq_length=10
        )
        print("生成的文本：", generated_text)
        
    except Exception as e:
        print(f"Error occurred: {e}")
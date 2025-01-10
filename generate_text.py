import torch
import torch.nn.functional as F
from typing import Dict, List, Optional
import numpy as np

def generate_text(model: torch.nn.Module, 
                 start_text: str, 
                 vocab: Dict[str, int], 
                 inv_vocab: Optional[Dict[int, str]] = None,
                 max_length: int = 50,
                 seq_length: int = 20,
                 temperature: float = 0.7,
                 top_k: int = 40) -> str:
    """
    改進的文本生成函數
    
    Args:
        model: 訓練好的語言模型
        start_text: 起始文本
        vocab: 詞彙表 (word -> id)
        inv_vocab: 反向詞彙表 (id -> word)
        max_length: 生成文本的最大長度
        seq_length: 序列長度
        temperature: 採樣溫度，控制生成文本的隨機性
        top_k: top-k 採樣的 k 值
    """
    # 創建反向詞彙表（如果沒有提供）
    if inv_vocab is None:
        inv_vocab = {v: k for k, v in vocab.items()}
    
    model.eval()
    words = start_text.lower().split()
    
    # 處理輸入序列
    input_ids = []
    for word in words:
        word_id = vocab.get(word, 0)
        word_id = min(word_id, model.vocab_size - 1)
        input_ids.append(word_id)
    
    # 如果輸入序列太短，用 0 填充
    if len(input_ids) < seq_length:
        padding = [0] * (seq_length - len(input_ids))
        input_ids = padding + input_ids
    
    input_seq = torch.tensor(input_ids[-seq_length:], dtype=torch.long).unsqueeze(0)
    
    # 生成文本
    generated_words = words.copy()
    with torch.no_grad():
        for _ in range(max_length):
            try:
                output = model(input_seq)
                
                # 應用溫度
                logits = output / temperature
                
                # 應用 top-k 採樣
                top_k_logits, top_k_indices = torch.topk(logits, k=min(top_k, logits.size(-1)))
                probs = F.softmax(top_k_logits, dim=-1)
                
                # 從 top-k 中採樣
                next_token_idx = torch.multinomial(probs, num_samples=1)
                next_word_id = top_k_indices[0][next_token_idx[0]].item()
                
                # 確保生成的 id 有對應的詞
                if next_word_id in inv_vocab:
                    next_word = inv_vocab[next_word_id]
                    generated_words.append(next_word)
                
                    # 更新輸入序列
                    input_ids = [vocab.get(w, 0) for w in generated_words[-seq_length:]]
                    input_seq = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0)
                else:
                    break
                    
            except Exception as e:
                print(f"Error during text generation: {e}")
                break
    
    return " ".join(generated_words)

def sample_response(model, user_input: str, vocab: Dict[str, int], 
                   inv_vocab: Dict[int, str]) -> str:
    """
    基於用戶輸入生成回應
    """
    try:
        response = generate_text(
            model=model,
            start_text=user_input,
            vocab=vocab,
            inv_vocab=inv_vocab,
            max_length=50,
            seq_length=20,
            temperature=0.7,
            top_k=40
        )
        return response
    except Exception as e:
        return f"抱歉，生成回應時出現錯誤：{str(e)}"

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
        vocab_size = max(1000, len(vocab) + 1)
        
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
        
        # 測試生成
        start_text = "你好"
        generated_text = generate_text(
            model=model,
            start_text=start_text,
            vocab=vocab,
            inv_vocab=inv_vocab
        )
        print("生成的文本：", generated_text)
        
    except Exception as e:
        print(f"Error occurred: {e}")
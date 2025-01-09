import re
#02_data_cleaning：清理和分詞
# 数据清理
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # 去除多余的空格
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    text = text.lower()  # 转为小写
    return text

# 示例
if __name__ == "__main__":
    from data_extraction import extract_pdf_text, extract_word_text

    pdf_text = extract_pdf_text("/Users/sma01/Downloads/testdata.pdf")
    word_text = extract_word_text("/Users/sma01/Downloads/testdata.docx")
    all_text = pdf_text + word_text
    cleaned_text = clean_text(all_text)
    print(cleaned_text[:500])

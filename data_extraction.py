from PyPDF2 import PdfReader
from docx import Document

#01_data extraction:從 PDF 和 Word 文件中提取文本
# 提取 PDF 文本
def extract_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# 提取 Word 文本
def extract_word_text(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# 示例：读取文件
if __name__ == "__main__":
    pdf_text = extract_pdf_text("/Users/sma01/Downloads/testdata.pdf")
    word_text = extract_word_text("/Users/sma01/Downloads/testdata.docx")
    all_text = pdf_text + word_text
    print(all_text[:500])  # 查看前 500 个字符


"""1. data_extraction.py：從 PDF 和 Word 文件中提取文本。
2. data_cleaning.py：清理和分詞。
3. tokenization.py：將文本轉換為 Token。
4. data_preparation.py：將 Token 序列切分為輸入和目標。
5. model.py：定義語言模型。
6. train.py：訓練模型。
7. save_load_model.py：保存和加載模型。
8. generate_text.py：生成文本。"""


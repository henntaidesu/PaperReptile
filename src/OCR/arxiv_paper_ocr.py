import ocrmypdf


def perform_ocr(input_pdf, output_pdf):
    options = {
        'language': 'eng',  # 指定OCR语言，可以根据需要更改
        'optimize': 1,  # 优化PDF输出
        'deskew': True,  # 对图像进行校正
    }

    ocrmypdf.ocr(input_pdf, output_pdf, **options)


if __name__ == "__main__":
    input_pdf_path = "input.pdf"  # 输入PDF文件的路径
    output_pdf_path = "output.pdf"  # 输出PDF文件的路径

    perform_ocr(input_pdf_path, output_pdf_path)

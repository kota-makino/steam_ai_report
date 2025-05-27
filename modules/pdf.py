from fpdf import FPDF
from io import BytesIO
import tempfile
import os
import re

def create_pdf(report_text, fig, title="Steamゲームデータ分析レポート", markdown=False):
    # 一時画像保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
        fig.savefig(tmp_img.name, format='png', bbox_inches='tight')
        tmp_img_path = tmp_img.name

    # PDF設定
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("IPAexG", "", "fonts/ipaexg.ttf", uni=True)
    pdf.add_font("IPAexG", "B", "fonts/ipaexg.ttf", uni=True)
    pdf.set_font("IPAexG", size=12)

    # タイトル
    pdf.set_font("IPAexG", size=16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(5)

    # グラフ
    pdf.image(tmp_img_path, x=15, w=180)
    pdf.ln(10)

    # レポート表示
    pdf.set_font("IPAexG", size=11)

    if markdown:
        lines = report_text.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                pdf.ln(2)
                continue
            if line.startswith("# "):
                pdf.set_font("IPAexG", "B", size=14)
                pdf.multi_cell(0, 8, line[2:].strip())
                pdf.set_font("IPAexG", size=11)
                pdf.ln(2)
            elif line.startswith("## "):
                pdf.set_font("IPAexG", "B", size=12)
                pdf.multi_cell(0, 8, line[3:].strip())
                pdf.set_font("IPAexG", size=11)
            elif line.startswith("- "):
                pdf.multi_cell(0, 8, "・" + line[2:].strip())
            elif re.match(r"\d+\. ", line):
                pdf.multi_cell(0, 8, "・" + line.strip())
            else:
                pdf.multi_cell(0, 8, line)
    else:
        text = report_text.replace("\n", " ")
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"([、。！？])", r"\1\n", text)
        paragraphs = [p.strip() for p in text.strip().split("\n") if p.strip()]
        for para in paragraphs:
            pdf.multi_cell(0, 8, para)
            pdf.ln(2)

    os.remove(tmp_img_path)
    pdf_buffer = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_buffer)

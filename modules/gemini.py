import tempfile
import os
from fpdf import FPDF
from io import BytesIO
import google.generativeai as genai
import streamlit as st

# Geminiの初期化
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

def create_prompt(df, countries, focus, custom_query):
    country_names = ", ".join(countries)
    return f"""
以下は {country_names} のSteamゲームデータに基づき、「{focus}」を分析するための情報です。
（使用データ件数: {len(df)}件）

{df.to_string(index=False)}

このデータをもとに以下を自然な日本語で分析してください：
- 傾向や相関関係
- 興味深いパターンや異常値
- 他国との比較や仮説（可能なら）

{custom_query or "気づいたことを自由に述べてください。"}
"""

def generate_summary(prompt):
    response = model.generate_content(prompt)
    return response.text

def create_pdf(report_text, fig):


    # 一時画像保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
        fig.savefig(tmp_img.name, format='png')
        tmp_img_path = tmp_img.name

    # PDF生成
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("ArialUnicode", "", "fonts/ipaexg.ttf", uni=True)
    pdf.set_font("ArialUnicode", size=12)
    pdf.multi_cell(0, 10, report_text)
    pdf.image(tmp_img_path, x=10, y=60, w=180)

    # PDFデータを文字列で取得
    pdf_output_str = pdf.output(dest='S').encode('latin1')  # binaryとして取得

    # BytesIOへ格納
    pdf_buffer = BytesIO(pdf_output_str)

    # 一時画像削除
    os.remove(tmp_img_path)

    return pdf_buffer
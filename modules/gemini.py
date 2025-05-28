import google.generativeai as genai
import streamlit as st


# Geminiの初期化
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")


def create_prompt(df, countries, focus, custom_query, markdown=False):
    country_names = ", ".join(countries)
    
    base_text = f"""
以下は {country_names} のSteamゲームデータに基づき、「{focus}」を分析するための情報です。
（使用データ件数: {len(df)}件）

{df.to_string(index=False)}

このデータをもとに以下を自然な日本語で分析してください：
- 傾向や相関関係
- 興味深いパターンや異常値
- 他国との比較や仮説（可能なら）

{custom_query or "気づいたことを自由に述べてください。"}
"""

    if markdown:
        base_text += "\n\n出力はMarkdown形式でお願いします（見出し、箇条書きなども含めて）。"

    return base_text


def generate_summary(prompt):
    response = model.generate_content(prompt)
    return response.text





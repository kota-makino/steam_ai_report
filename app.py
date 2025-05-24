import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from io import BytesIO
from fpdf import FPDF
import tempfile
import os
import google.generativeai as genai

# Geminiの初期化
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# 利用可能な国コード
COUNTRIES = ["jp", "us", "kr", "de"]

# 切り口（分析視点）
FOCUS_OPTIONS = [
    "レビュー数",
    "リリース年",
    "無料かどうか",
    "年齢制限",
    "開発会社",
    "プラットフォーム"
]

plt.rcParams['font.family'] = 'Meiryo'  # ← ここで日本語フォントを指定
plt.rcParams['axes.unicode_minus'] = False  # ← マイナス符号の文字化け対策


@st.cache_data
def load_data():
    conn = sqlite3.connect("data/steam_games.db")
    df = pd.read_sql_query("SELECT * FROM games", conn)
    conn.close()
    return df

def filter_data(df, countries):
    return df[df["country"].isin(countries)].copy()

def prepare_ai_input(df, focus):
    if focus == "年齢制限":
        return df.groupby("required_age").agg(
            ゲーム数=("appid", "count"),
            平均価格=("price", "mean"),
            平均レビュー数=("recommendations", "mean")
        ).reset_index()
    elif focus == "無料かどうか":
        return df.groupby("is_free").agg(
            ゲーム数=("appid", "count"),
            平均価格=("price", "mean"),
            平均レビュー数=("recommendations", "mean")
        ).reset_index()
    elif focus == "プラットフォーム":
        platforms = df["platforms"].dropna().str.get_dummies(sep=", ").sum().sort_values(ascending=False)
        return pd.DataFrame({"プラットフォーム": platforms.index, "ゲーム数": platforms.values})
    elif focus == "開発会社":
        return df["developers"].value_counts().head(20).reset_index().rename(columns={"index": "開発会社", "developers": "ゲーム数"})
    elif focus == "価格":
        return df.sort_values("price").head(50)
    elif focus == "レビュー数":
        return df.sort_values("recommendations", ascending=False).head(50)
    elif focus == "リリース年":
        df["year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
        return df.dropna(subset=["year"])
    else:
        return df.head(50)

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

def draw_graph(df, focus):
    fig, ax = plt.subplots(figsize=(10, 6))

    if focus == "価格":
        sns.histplot(df[df["price"] > 0], x="price", bins=30, ax=ax)
        ax.set_title(f"価格分布（{len(df)}件）")
    elif focus == "レビュー数":
        sns.histplot(df[df["recommendations"] > 0], x="recommendations", bins=30, ax=ax)
        ax.set_title(f"レビュー数分布（{len(df)}件）")
    elif focus == "リリース年":
        sns.histplot(df["year"].dropna(), bins=20, ax=ax)
        ax.set_title(f"リリース年の分布（{len(df)}件）")
    elif focus == "無料かどうか":
        sns.countplot(data=df, x="is_free", ax=ax)
        ax.set_title(f"無料/有料の分布（{len(df)}件）")
    elif focus == "年齢制限":
        sns.barplot(data=df, x="required_age", y="ゲーム数", ax=ax)
        ax.set_title(f"年齢制限別の本数（{len(df)}件）")
    elif focus == "開発会社":
        sns.barplot(data=df, y="開発会社", x="ゲーム数", ax=ax)
        ax.set_title(f"上位20開発会社の本数（{len(df)}件）")
    elif focus == "プラットフォーム":
        sns.barplot(data=df, y="プラットフォーム", x="ゲーム数", ax=ax)
        ax.set_title(f"プラットフォームの対応状況（{len(df)}件）")

    st.pyplot(fig)
    return fig

def create_pdf(report_text, fig):
    import tempfile
    import os

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


st.title("🎮 Steamデータ分析AIレポート - Gemini対応")

with st.sidebar:
    countries = st.multiselect("対象国を選択", options=COUNTRIES, default=["jp"])
    focus = st.selectbox("分析の切り口を選択", options=FOCUS_OPTIONS)
    user_query = st.text_input("AIに追加で聞きたいこと（任意）", placeholder="例：この傾向が生まれた理由を教えて")

if st.button("🧠 レポートを生成"):
    with st.spinner("データを準備中..."):
        raw_df = load_data()
        filtered_df = filter_data(raw_df, countries)

        if filtered_df.empty:
            st.error("データが見つかりませんでした。")
        else:
            df_subset = prepare_ai_input(filtered_df, focus)
            prompt = create_prompt(df_subset, countries, focus, user_query)
            report_text = generate_summary(prompt)

            st.subheader("🔍 AIによる分析レポート")
            fig = draw_graph(df_subset, focus)
            st.write(report_text)




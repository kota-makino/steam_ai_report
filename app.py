import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from io import BytesIO
from fpdf import FPDF
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

def create_prompt(df, countries, focus, custom_query):
    country_names = ", ".join(countries)
    return f"""
以下は {country_names} のSteamゲームデータです。

{df.to_string(index=False)}

あなたは優秀なゲームアナリストです。
次の切り口「{focus}」に着目し、以下の視点で自然な日本語で分析を出力してください：

- データから見えてくる傾向や相関関係
- 異常値や興味深いパターン
- 他の国と比較して目立つ点
- 将来的な展望や仮説

{custom_query or "自由に解釈を広げてください。"}
"""

def generate_summary(prompt):
    response = model.generate_content(prompt)
    return response.text

def draw_graph(df, focus):
    fig, ax = plt.subplots(figsize=(10, 6))


    if focus == "レビュー数":
        sns.barplot(data=df, x="recommendations", y="name", ax=ax)
        ax.set_title("レビュー数が多い順（上位20件）")
    elif focus == "リリース年":
        df["year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
        sns.histplot(df["year"].dropna(), bins=20, ax=ax)
        ax.set_title("リリース年の分布")
    elif focus == "無料かどうか":
        sns.countplot(data=df, x="is_free", ax=ax)
        ax.set_title("無料/有料の分布")
    elif focus == "年齢制限":
        sns.countplot(data=df, x="required_age", ax=ax)
        ax.set_title("年齢制限別の本数")
    elif focus == "開発会社":
        top_dev = df["developers"].value_counts().head(20)
        sns.barplot(x=top_dev.values, y=top_dev.index, ax=ax)
        ax.set_title("上位20開発会社の本数")
    elif focus == "プラットフォーム":
        platforms = df["platforms"].dropna().str.get_dummies(sep=", ").sum().sort_values(ascending=False)
        sns.barplot(x=platforms.values, y=platforms.index, ax=ax)
        ax.set_title("プラットフォームの対応状況")

    st.pyplot(fig)
    return fig

def create_pdf(report_text, fig):
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("ArialUnicode", "", "fonts/ipaexg.ttf", uni=True)
    pdf.set_font("ArialUnicode", size=12)
    pdf.multi_cell(0, 10, report_text)
    pdf.image(img_buffer, x=10, y=60, w=180)

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
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
            # レポートとグラフに使う同じデータを作る
            if focus == "価格":
                df_subset = filtered_df.sort_values("price").head(20)
            elif focus == "レビュー数":
                df_subset = filtered_df.sort_values("recommendations", ascending=False).head(20)
            elif focus == "開発会社":
                df_subset = filtered_df.copy()
            elif focus == "プラットフォーム":
                df_subset = filtered_df.copy()
            elif focus == "無料かどうか":
                df_subset = filtered_df.copy()
            elif focus == "年齢制限":
                df_subset = filtered_df.copy()
            elif focus == "リリース年":
                df_subset = filtered_df.copy()
            else:
                df_subset = filtered_df.head(50)

            prompt = create_prompt(df_subset, countries, focus, user_query)
            report_text = generate_summary(prompt)

            st.subheader("🔍 AIによる分析レポート")
            st.write(report_text)

            fig = draw_graph(df_subset, focus)

            pdf_file = create_pdf(report_text, fig)
            st.download_button("📄 PDFレポートをダウンロード", pdf_file, file_name="steam_ai_report.pdf", mime="application/pdf")

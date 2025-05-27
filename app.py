# app.py（本体）
import streamlit as st
from modules.data_loader import load_data, filter_data, prepare_ai_input
from modules.graph import draw_graph
from modules.gemini import create_prompt, generate_summary
from modules.pdf import create_pdf
from matplotlib import pyplot as plt, font_manager as fm

# UI設定
def main():
    st.title("🎮 Steamデータ分析AIレポート - Gemini対応")

    COUNTRIES = ["jp", "us", "kr", "de"]
    FOCUS_OPTIONS = [
        "価格",
        "レビュー数",
        "リリース年",
        "無料かどうか",
        "年齢制限",
        "開発会社",
        "プラットフォーム"
    ]

    # フォントの設定
    plt.rcParams['font.family'] = 'Meiryo'  
    plt.rcParams['axes.unicode_minus'] = False  
    fm.fontManager.addfont("fonts/ipaexg.ttf")
    plt.rcParams["font.family"] = "IPAexGothic"

    with st.sidebar:
            countries = st.multiselect("対象国を選択", options=COUNTRIES, default=["jp"])
            focus = st.selectbox("分析の切り口を選択", options=FOCUS_OPTIONS)
            user_query = st.text_input("AIに追加で聞きたいこと（任意）", placeholder="例：この傾向が生まれた理由を教えて")

    # セッション初期化
    if "report_text" not in st.session_state:
        st.session_state.report_text = ""
        st.session_state.prompt = ""
        st.session_state.fig = None

    if st.button("🧠 レポートを生成"):
        with st.spinner("データを準備中..."):
            raw_df = load_data()
            filtered_df = filter_data(raw_df, countries)

            if filtered_df.empty:
                st.error("データが見つかりませんでした。")
            else:
                df_subset = prepare_ai_input(filtered_df, focus)
                prompt = create_prompt(df_subset, countries, focus, user_query, markdown=True)
                report_text = generate_summary(prompt)
                fig = draw_graph(df_subset, focus)

                # セッションに保存
                st.session_state.report_text = report_text
                st.session_state.prompt = prompt
                st.session_state.fig = fig

    # 表示（ボタン外でも維持）
    if st.session_state.report_text:

        st.subheader("📊 グラフ")
        st.pyplot(st.session_state.fig)

        st.subheader("🔍 AIによる分析レポート")
        st.markdown(st.session_state.report_text)

        pdf_file = create_pdf(
            st.session_state.report_text,
            st.session_state.fig,
            markdown=True
        )
        st.download_button("📄 PDFレポートをダウンロード", pdf_file, file_name="steam_ai_report.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()




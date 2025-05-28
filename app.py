# app.py（本体）
import streamlit as st
from modules.data_loader import load_data, filter_data, prepare_ai_input
from modules.graph import set_fonts,draw_graph
from modules.gemini import create_prompt, generate_summary
from modules.pdf import create_pdf
from config.settings import COUNTRIES, FOCUS_OPTIONS


# UI設定
def main():
    st.title("🎮 Steamジャンル傾向分析AIレポート")

    set_fonts()

    with st.sidebar:
        countries = st.multiselect("対象国を選択", options=COUNTRIES, default=["jp"])
        focus = st.selectbox("分析の切り口を選択", options=FOCUS_OPTIONS)
        user_query = st.text_input("AIに追加で聞きたいこと（任意）", placeholder="例：なぜこの傾向があるの？")
        button = st.button("🧠 レポートを生成")

    # セッション初期化
    if "report_text" not in st.session_state:
        st.session_state.report_text = ""
        st.session_state.prompt = ""
        st.session_state.fig = None
        st.session_state.recommend = ""


    if button:
        with st.spinner("データを準備中..."):
            raw_df = load_data()
            filtered_df = filter_data(raw_df, countries)
            
            if filtered_df.empty:
                st.error("データが見つかりませんでした。")
            else:
                df_subset = prepare_ai_input(filtered_df, focus)
                
                # グラフを作成
                fig = draw_graph(df_subset, focus)
                
                # プロンプト作成とAI分析
                prompt = create_prompt(df_subset, countries, focus, user_query, markdown=True)
                report_text = generate_summary(prompt)
                
                # セッション状態に保存
                st.session_state.report_text = report_text
                st.session_state.prompt = prompt
                st.session_state.fig = fig

    # 表示部分
    if st.session_state.report_text:
        st.subheader("📊 ジャンル別分布グラフ")
        
        # グラフが存在する場合のみ表示
        if st.session_state.fig is not None:
            st.pyplot(st.session_state.fig)
        else:
            st.error("グラフの作成に失敗しました。")
        
        st.subheader("🧠 Geminiによる日本語要約")
        st.markdown(st.session_state.report_text)
        
        # PDF作成時もグラフを含める
        if st.session_state.fig is not None:
            pdf_file = create_pdf(
                st.session_state.report_text,
                st.session_state.fig,
                markdown=True
            )
            st.download_button("📄 PDFレポートをダウンロード", pdf_file, 
                            file_name="steam_ai_report.pdf", mime="application/pdf")
if __name__ == "__main__":
    main()




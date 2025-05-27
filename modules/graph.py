import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import pyplot as plt, font_manager as fm

 # フォントの設定
def set_fonts():
    plt.rcParams['font.family'] = 'Meiryo'  
    plt.rcParams['axes.unicode_minus'] = False  
    fm.fontManager.addfont("fonts/ipaexg.ttf")
    plt.rcParams["font.family"] = "IPAexGothic"


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

    return fig
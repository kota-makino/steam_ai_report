

import matplotlib.pyplot as plt
from matplotlib import pyplot as plt, font_manager as fm
import pandas as pd

def plot_price_pie(df):
    """価格の円グラフ（無料 vs 有料、有料内価格帯）"""
    plt.close('all')  # 既存の図をクリア
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # デバッグ用: データの確認
    #print(f"データフレームの形状: {df.shape}")
    #print(f"price_jpy列の存在確認: {'price_jpy' in df.columns}")
    #if 'price_jpy' in df.columns:
        #print(f"価格データのサンプル: {df['price_jpy'].head()}")
        #print(f"価格データの統計: {df['price_jpy'].describe()}")
    
    try:
        # price_jpy列が存在しない場合の対処
        if 'price_jpy' not in df.columns:
            # 代替として price 列を使用するか、エラーメッセージを表示
            if 'price' in df.columns:
                df['price_jpy'] = df['price']  # 一時的にコピー
            else:
                axes[0].text(0.5, 0.5, "価格データが見つかりません", 
                           ha='center', va='center', transform=axes[0].transAxes)
                axes[1].text(0.5, 0.5, "価格データが見つかりません", 
                           ha='center', va='center', transform=axes[1].transAxes)
                axes[0].set_title("価格データなし")
                axes[1].set_title("価格データなし")
                return fig
        
        # 全体の無料・有料構成
        free_count = (df["price_jpy"] == 0).sum()
        paid_count = (df["price_jpy"] > 0).sum()
        total_count = free_count + paid_count
        
        #print(f"無料ゲーム数: {free_count}, 有料ゲーム数: {paid_count}")
        
        if total_count == 0:
            axes[0].text(0.5, 0.5, "データがありません", 
                       ha='center', va='center', transform=axes[0].transAxes)
            axes[1].text(0.5, 0.5, "データがありません", 
                       ha='center', va='center', transform=axes[1].transAxes)
        else:
            # 左側の円グラフ: 無料 vs 有料
            if free_count > 0 and paid_count > 0:
                wedges, texts, autotexts = axes[0].pie(
                    [free_count, paid_count], 
                    labels=["無料", "有料"], 
                    autopct='%1.1f%%', 
                    startangle=90,
                    colors=['lightblue', 'lightcoral']
                )
            elif free_count > 0:
                wedges, texts, autotexts = axes[0].pie(
                    [free_count], 
                    labels=["無料"], 
                    autopct='%1.1f%%', 
                    startangle=90,
                    colors=['lightblue']
                )
            else:
                wedges, texts, autotexts = axes[0].pie(
                    [paid_count], 
                    labels=["有料"], 
                    autopct='%1.1f%%', 
                    startangle=90,
                    colors=['lightcoral']
                )
            
            axes[0].set_title(f"全ゲーム：無料 vs 有料 (総数: {total_count})")

            # 右側の円グラフ: 有料ゲームの価格帯分布
            paid_df = df[df["price_jpy"] > 0].copy()
            
            if len(paid_df) > 0:
                bins = [0, 500, 1000, 2000, 4000, 8000, float('inf')]
                labels = ["〜500円", "501〜1000円", "1001〜2000円", 
                         "2001〜4000円", "4001〜8000円", "8001円〜"]
                
                paid_df["price_bin"] = pd.cut(paid_df["price_jpy"], bins=bins, 
                                            labels=labels, right=True)
                price_counts = paid_df["price_bin"].value_counts().sort_index()
                
                # 0でない値のみをプロット
                price_counts = price_counts[price_counts > 0]
                
                print(f"価格帯別カウント: {price_counts}")
                
                if len(price_counts) > 0:
                    colors = ['gold', 'lightgreen', 'salmon', 'skyblue', 'plum', 'orange']
                    wedges, texts, autotexts = axes[1].pie(
                        price_counts.values, 
                        labels=price_counts.index, 
                        autopct='%1.1f%%', 
                        startangle=90,
                        colors=colors[:len(price_counts)]
                    )
                    axes[1].set_title(f"有料ゲーム：価格帯分布 (総数: {len(paid_df)})")
                else:
                    axes[1].text(0.5, 0.5, "価格帯データなし", 
                               ha='center', va='center', transform=axes[1].transAxes)
                    axes[1].set_title("価格帯分布なし")
            else:
                axes[1].text(0.5, 0.5, "有料ゲームがありません", 
                           ha='center', va='center', transform=axes[1].transAxes)
                axes[1].set_title("有料ゲームなし")
        
        # 軸の設定を明示的に行う
        for ax in axes:
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)
            ax.set_aspect('equal')
        
    except Exception as e:
        print(f"グラフ作成エラー: {e}")
        import traceback
        traceback.print_exc()
        
        axes[0].text(0.5, 0.5, f"エラーが発生しました: {str(e)}", 
                   ha='center', va='center', transform=axes[0].transAxes)
        axes[1].text(0.5, 0.5, f"エラーが発生しました: {str(e)}", 
                   ha='center', va='center', transform=axes[1].transAxes)
    
    plt.tight_layout()
    return fig
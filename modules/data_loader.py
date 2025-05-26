import sqlite3
import pandas as pd
import streamlit as st

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
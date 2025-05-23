import requests
import time
import os
import json
from datetime import datetime, timedelta
import pandas as pd

# 人気AppIDリストをCSVから読み込み（カラム: appid, name）
def load_popular_appids(csv_path="data/popular_appids.csv", limit=500):
    df = pd.read_csv(csv_path)
    return df.head(limit).to_dict(orient="records")

# AppIDと国コードを指定して詳細情報を取得
def fetch_app_details(appid, country_code):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc={country_code}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# recommendations が一定以上か確認
def has_enough_recommendations(data, appid, threshold):
    try:
        return data[str(appid)]["data"].get("recommendations", {}).get("total", 0) >= threshold
    except:
        return False

# JSONファイルとして保存（appid_国コード.json）
def save_json(appid, country_code, data, folder="data/raw_games_base"):
    os.makedirs(folder, exist_ok=True)
    filename = f"{appid}_{country_code}.json"
    with open(os.path.join(folder, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ファイルが24時間以内に更新済みかチェック
def is_recently_updated(appid, country_code, folder="data/raw_games_base"):
    filename = f"{appid}_{country_code}.json"
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        return (datetime.now() - modified_time) < timedelta(hours=24)
    return False

if __name__ == "__main__":
    apps = load_popular_appids("data/popular_appids.csv")

    country_codes = ["jp", "us", "kr", "de"]

    recomend_count = 1

    for country in country_codes:
        print(f"🌍 {country} 用の人気アプリを取得中...")
        for app in apps:
            appid = app["appid"]
            name = app["name"]
            if is_recently_updated(appid, country):
                print(f"⏭️ {appid}_{country}.json は最近更新済み。スキップ")
                continue
            print(f"📦 {appid}: {name} [{country}] → 取得中")
            data = fetch_app_details(appid, country)
            if data and data.get(str(appid), {}).get("success") and has_enough_recommendations(data, appid,recomend_count):
                save_json(appid, country, data)
                print(f"✅ 保存完了（レビュー{recomend_count}件以上）")
            else:
                print(f"❌ スキップ（レビュー不足または取得失敗）")
            time.sleep(1)

    print("✅ 人気AppIDベースの取得完了")

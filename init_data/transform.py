import os
import json
import pandas as pd
import sqlite3

# 必要な情報だけ抽出する関数
def extract_info(appid, data, country_code):
    try:
        app_data = data[str(appid)]['data']
        return {
            'appid': appid,
            'name': app_data.get('name'),
            'price': app_data.get('price_overview', {}).get('final', 0) / 100,
            'genres': ', '.join([g['description'] for g in app_data.get('genres', [])]),
            'release_date': app_data.get('release_date', {}).get('date'),
            'recommendations': app_data.get('recommendations', {}).get('total', 0),
            'developers': ', '.join(app_data.get('developers', [])),
            'publishers': ', '.join(app_data.get('publishers', [])),
            'platforms': ', '.join([k for k, v in app_data.get('platforms', {}).items() if v]),
            'required_age': app_data.get('required_age', 0),
            'is_free': app_data.get('is_free', False),
            'country': country_code
        }
    except:
        return None

# JSONファイルから整形してSQLiteに保存
# ファイル名が appid_国コード.json の形式である前提
def transform_all_to_sqlite(json_folder, conn):
    records = []

    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            parts = filename.replace(".json", "").split("_")
            appid = parts[0]
            country = parts[1] if len(parts) > 1 else "unknown"
            with open(os.path.join(json_folder, filename), encoding="utf-8") as f:
                data = json.load(f)
                record = extract_info(appid, data, country)
                if record:
                    records.append(record)

    if records:
        df = pd.DataFrame(records)
        df.to_sql("games", conn, if_exists='replace', index=False)
        print(f"✅ {len(records)} 件のデータをDBに保存しました。")

if __name__ == "__main__":
    db_path = "data/steam_games.db"
    json_folder = "data/raw_games_base"
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(db_path)
    transform_all_to_sqlite(json_folder, conn)
    conn.close()
    print("✅ すべてのデータをデータベースに保存しました。")

import streamlit as st
import feedparser
import json
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup



# JSONファイルからRSSフィードのデータを読み込む
def load_rss_feeds(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# RSSフィードのデータをJSONファイルに保存する
def save_rss_feeds(file_path, rss_feeds):
    with open(file_path, "w") as file:
        json.dump(rss_feeds, file)

def get_feed_titles(feed_urls):
    titles = {}
    for url in feed_urls:
        feed = feedparser.parse(url)
        title = feed.feed.get("title", url)  # タイトルがない場合はURLを使用
        titles[url] = title
    return titles

def load_favorites(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_favorites(file_path, favorites_list):
    with open(file_path, "w") as file:
        json.dump(favorites_list, file)

favorites_file_path = "favorites.json"
if "favorites" not in st.session_state:
    st.session_state.favorites = load_favorites(favorites_file_path)
#favorites = load_favorites(favorites_file_path)




# ファイルパスの設定
rss_file_path = "rss_feeds.json"
rss_feeds = load_rss_feeds(rss_file_path)
favorites = []



#メインページの内容

page = st.sidebar.selectbox("ページを選択", ["メイン", "お気に入り", "URLからRSSを作成", "管理画面"])
if page == "メイン":
    # Streamlitページの設定
    st.title("記事一覧")

    #スライダーの設定
    # RSSフィードのURLを入力
    with st.sidebar:
        st.header("RSSフィードの追加")
        new_feed_url = st.text_input("RSSフィードのURLを入力してください")
        update_interval = st.selectbox("更新間隔を選択してください", options=["15分", "30分", "1時間", "2時間", "6時間"])
        if st.button("フィードを追加"):
            if new_feed_url not in rss_feeds:
                feed = feedparser.parse(new_feed_url)
                feed_title = feed.feed.title  # RSSフィードのタイトルを取得
                # 画像のURLを取得
                if hasattr(feed.entries[0], 'image'):
                    feed_image_url = feed.entries[0].image
                elif hasattr(feed.entries[0], 'media_content'):
                    feed_image_url = feed.entries[0].media_content[0]['url']
                elif hasattr(feed.entries[0], 'media_thumbnail'):
                    feed_image_url = feed.entries[0].media_thumbnail[0]['url']
                else:
                    feed_image_url = None
                rss_feeds[new_feed_url] = {"title": feed_title,  "image_url": feed_image_url,"interval": update_interval, "last_updated": str(datetime.now())}
                save_rss_feeds(rss_file_path, rss_feeds)

      # フィードの表示順序を変更
    st.header("表示順序の変更")
    # 既存のRSSフィードのURLリストからタイトルを取得
    feed_titles = get_feed_titles(list(rss_feeds.keys()))

    # フィードの選択ウィジェットを修正
    feed_order = st.multiselect(
        "表示するRSSフィードを選択してください",
        options=list(feed_titles.values()),  # タイトルを表示
        default=list(feed_titles.values())
    )

    # 選択されたタイトルに基づいてURLを取得
    selected_feeds = [url for url, title in feed_titles.items() if title in feed_order]
    search_query = st.text_input("記事を検索")
    # フィードの記事を表示
    for feed_url in selected_feeds:
        feed = feedparser.parse(feed_url)
        feed_title = feed.feed.title
        st.subheader(feed.feed.title)



        for entry in feed.entries:
            # link属性の存在を確認し、存在しない場合は代替テキストを使用
            entry_link = entry.link if hasattr(entry, 'link') else "#"
            entry_key = f"{entry.title}-{entry_link}"  # エントリのタイトルとリンクを組み合わせてキーを生成
            # 検索クエリとタイトルの一致をチェック
            if search_query.lower() in entry.title.lower():
                    
            # 画像URLを取得
                image_url = entry.image if hasattr(entry, 'image') else None
                

               

                if image_url:
                    st.image(image_url, width=300)


                    # 記事タイトルにリンクを埋め込む
                st.markdown(f"[{entry.title}]({entry_link})", unsafe_allow_html=True)
                    # お気に入りに追加するボタン
                if st.button("お気に入りに追加", key=entry_key):
                        fav_entry = {
                            'title': entry.title,
                            'link': entry_link,
                            'image_url': image_url,
                            'source': feed_title,
                            'added_date': datetime.now().isoformat()
                        }
                        st.session_state.favorites.append(fav_entry)
                        save_favorites(favorites_file_path, st.session_state.favorites)

elif page == "お気に入り":
    source_options = list(set([fav.get('source', '不明') for fav in st.session_state.favorites]))
    selected_source = st.sidebar.selectbox("記事媒体を選択", ["すべて表示"] + source_options)

    # 選択された媒体に基づいてタイトルを設定
    display_title = f"お気に入り記事 - {selected_source}" if selected_source != "すべて表示" else "お気に入り記事"
    st.title(display_title)

    for index, fav in enumerate(st.session_state.favorites):
        if selected_source == "すべて表示" or fav.get('source') == selected_source:
            st.markdown(f"[{fav['title']}]({fav['link']})", unsafe_allow_html=True)

            if fav.get('image_url'):
                st.image(fav['image_url'], width=300)

            if st.button("お気に入りから削除", key=f"{fav['link']}-{index}"):
                st.session_state.favorites.remove(fav)
                save_favorites(favorites_file_path, st.session_state.favorites)

elif page == "URLからRSSを作成":
    st.title('URLからRSSを作成する外部サイト')
    st.markdown('以下のリンクから [happyou.info/fs](https://happyou.info/fs/) サイトにアクセスできます。')

    # リンクを表示
    st.write('happyou.info/fs: [こちらをクリック](https://happyou.info/fs/)')





elif page == "管理画面":
    st.title("管理画面")

    # RSSフィードの情報を表形式で表示
    rss_data = []
    for url, feed_info in rss_feeds.items():
        rss_data.append({
            "媒体名": feed_info.get('title', '不明'),  # RSSフィードのタイトルを取得
            "URL": url,
            "最終更新": feed_info.get('last_updated', '不明'),
            "削除": url
        })
    # データフレームを作成
    df = pd.DataFrame(rss_data)

    # 表を表示
    for index, row in df.iterrows():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.text(row['媒体名'])
        with col2:
            st.text(row['URL'])
        with col3:
            st.text(row['最終更新'])
        with col4:
            if st.button("削除", key=row['削除']):
                del rss_feeds[row['削除']]
                save_rss_feeds(rss_file_path, rss_feeds)
                st.experimental_rerun()

# 以下は以前のelifページが"メイン"のコード

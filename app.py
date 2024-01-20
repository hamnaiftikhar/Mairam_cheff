import numpy as np
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
import random

api_key = 'AIzaSyCEVvQd8_9EwmKnYoOhfxTVe8hQto9Tl_Q'

df = pd.read_csv("./filtered.csv")
temp = []
t = []
for i in df["FilteredIngredients"]:
    temp.extend(i.split(" "))
    t.append(i.split(" "))
cho = set(temp)
df["FilteredIngredients"] = t

def youtube_search(api_key, query, max_results=1):
    youtube = build('youtube', 'v3', developerKey=api_key)

    search_response = youtube.search().list(
        q=query,
        type='video',
        part='id,snippet',
        maxResults=max_results
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        video_response = youtube.videos().list(
            id=video_id,
            part='snippet,statistics'
        ).execute()

        video_info = video_response['items'][0]['snippet']
        video_statistics = video_response['items'][0]['statistics']

        video = {
            'title': video_info['title'],
            'views': video_statistics['viewCount'],
            'link': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': video_info['thumbnails']['default']['url']
        }

        videos.append(video)

    return videos

def selection_page():
    global options
    st.title("Selection Page")
    options = st.multiselect("Select Available Ingredients: ", cho)
    if st.button("Confirm"):
        # Finding top 5 matches
        df['MatchCount'] = df['FilteredIngredients'].apply(lambda x: len(set(x) & set(options)))
        top_matches = df.nlargest(5, 'MatchCount')

        st.markdown("---")
        st.markdown("## Results")

        for i in top_matches['TranslatedRecipeName']:
            expander = st.expander(i)
            with expander:
                selected_rows = np.array(top_matches[top_matches['TranslatedRecipeName'] == i])

                st.write(f"Time to cook: {selected_rows[0][1]} mins")
                st.write(f"Servings: {selected_rows[0][2]}")
                st.write(f"Cuisine: {selected_rows[0][3]}")
                st.write(f"Course: {selected_rows[0][5]}")
                st.write(f"URL: {selected_rows[0][6]}")

                search_query = f"how to make {str(i).replace("_", " ")} at home"
                results = youtube_search(api_key, search_query)

                st.write("Youtube: ")

                for result in results:
                    st.write(f"Title: {result['title']}")
                    st.write(f"Views: {result['views']}")
                    st.write(f"Link: {result['link']}")

        recommendation = [random.choice(df['TranslatedRecipeName']) for _ in range(5)]

        st.markdown("---")
        st.markdown("## Recommendations:")

        for i in recommendation:
            expander = st.expander(i)
            with expander:
                selected_rows = np.array(df[df['TranslatedRecipeName'] == i])

                st.write(f"Time to cook: {selected_rows[0][1]} mins")
                st.write(f"Servings: {selected_rows[0][2]}")
                st.write(f"Cuisine: {selected_rows[0][3]}")
                st.write(f"Course: {selected_rows[0][5]}")
                st.write(f"URL: {selected_rows[0][6]}")

                search_query = f"how to make {str(i).replace("_", " ")} at home"
                results = youtube_search(api_key, search_query)

                st.write("Youtube: ")

                for result in results:
                    st.write(f"Title: {result['title']}")
                    st.write(f"Views: {result['views']}")
                    st.write(f"Link: {result['link']}")

            
if __name__ == "__main__":
    selection_page()

"""
Step 1: Log into YouTube
Step 2: Grab playlist video titles
Step 3: Store video titles in .txt file
"""

import json
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests

class LogPlaylist:
    def __init__(self, playlist_id):
        self.videos = {}
        self.playlist_id = playlist_id
        self.youtube_client = self.get_youtube_client()

    def get_youtube_client(self):
        """ Log into YouTube, copied from YouTube Data API """
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # From YT Data API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client

    def get_playlist_titles(self):
        """ Stores playlist video titles and link into a dictionary """
        response = self.request_playlist()
        
        # Collect each video in the playlist and get title
        for item in response["items"]:
            self.videos[item["snippet"]["title"]] = "https://www.youtube.com/watch?v={}".format(item["contentDetails"]["videoId"])

        # Collect additional videos
        while "nextPageToken" in response:
            response = self.request_playlist(response["nextPageToken"])

            for item in response["items"]:
                self.videos[item["snippet"]["title"]] = "https://www.youtube.com/watch?v={}".format(item["contentDetails"]["videoId"])


    def request_playlist(self, next_page_token=None):
        """ Grab playlist video titles """
        if next_page_token is None:
            request = self.youtube_client.playlistItems().list(
                part="snippet, contentDetails",
                maxResults=50,
                playlistId=self.playlist_id
            )
            response = request.execute()
        else:
            request = self.youtube_client.playlistItems().list(
                part="snippet, contentDetails",
                maxResults=50,
                pageToken=next_page_token,
                playlistId=self.playlist_id
            )
            response = request.execute()
        return response

    def store_titles(self):
        """ Store video titles in .txt file """
        log = open("log.txt", "w", encoding="utf-8")
        str_log = "[DATE HERE]\n"
        for video in self.videos:
            str_log += str(video) + " " + str(self.videos[video]) + "\n"
        log.write(str_log)
        log.close()

if __name__ == '__main__':
    lp = LogPlaylist("PLPKBNgKUrDv5VaWps6FHMGtxevOToWQQa")
    lp.get_playlist_titles()
    print(lp.videos)
    lp.store_titles()

    # test = {1:'a',2:'b',3:'c'}
    # file = open("test.txt", "w", encoding="utf-8")
    # str_log = "ルシカ"
    # for num in test:
    #     str_log += str(num) + " " + str(test[num])
    # file.write(str_log)
    # file.close()
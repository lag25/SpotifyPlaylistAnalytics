import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.express as px
from datetime import datetime
from collections import defaultdict

# Spotify API credentials
CLIENT_ID = 'd19a543944aa42428033b5195bd80a16'
CLIENT_SECRET = '665d6ca252f148dfba5ab2b05e1d9fe7'


# Function to authenticate with the Spotify API
def authenticate_spotify():
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp


# Function to get playlist tracks and their added timestamps
def get_playlist_data(sp, playlist_uri):
    playlist_id = playlist_uri.split(':')[-1]

    # Get the first set of tracks
    playlist_info = sp.playlist_tracks(playlist_id, limit=100)

    track_data = []
    for track in playlist_info['items']:
        added_at = datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
        track_data.append(added_at)

    # Check if there are more tracks
    while playlist_info['next']:
        playlist_info = sp.next(playlist_info)
        for track in playlist_info['items']:
            added_at = datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
            track_data.append(added_at)

    min_date = min(track_data)
    days_since_creation = [(date - min_date).days for date in track_data]
    unique_vals = set(days_since_creation)
    hashMap = defaultdict(int)
    for i in unique_vals:
        hashMap[i] = days_since_creation.count(i)

    return (hashMap, unique_vals)


# Function to plot the bar graph using Plotly
def plot_bar_graph(track_data):
    fig = px.bar(x=track_data[0].keys(), y=track_data[0].values(),
                 labels={'x': 'Days Since Creation', 'y': 'Number of songs added'},
                 title='Playlist Growth Over Time', orientation='v')

    return fig


def plot_line_graph(track_data):
    LAST = 0
    hashMap = {}  # Initialize a dictionary to store cumulative counts
    for i in track_data[1]:
        LAST += hashMap[i]  # Add the count of the current track to the last count
        hashMap[i] = LAST  # Update the cumulative count for the current track

    # Create a line plot
    fig = px.line(x=hashMap.keys(), y=hashMap.values(), title='Cumulative Playlist Growth Over Time')
    fig.update_layout(xaxis_title='Days Since Creation', yaxis_title='Cumulative Number of songs added')

    return fig


# Streamlit App


def main():
    st.title("Spotify Playlist Analytics")

    playlist_uri = st.text_input("Enter Spotify Playlist URI:")
    if not playlist_uri.startswith("spotify:playlist:"):
        st.warning("Please enter a valid Spotify Playlist URI.")
        st.stop()

    sp = authenticate_spotify()
    track_data = get_playlist_data(sp, playlist_uri)

    if not track_data:
        st.warning("Unable to fetch playlist data. Please check your URI or try again later.")
        st.stop()

    bt1 = st.button("LINE PLOT")
    bt2 = st.button("BAR PLOT")
    if bt1:
        st.plotly_chart(plot_line_graph(track_data), use_container_width=True)
    if bt2:
        st.plotly_chart(plot_bar_graph(track_data), use_container_width=True)
    # Display the bar graph


if __name__ == "__main__":
    main()

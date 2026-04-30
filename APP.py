import html

import pandas as pd
import plotly.express as px
import streamlit as st


# Configure the Streamlit page before any other Streamlit output is rendered.
st.set_page_config(
    page_title="Big Four Thrash Dashboard",
    layout="wide",
)


# Store reusable app settings in one place so they are easy to change later.
DATA_PATH = "big4_tracks_with_bpm_clean.csv"
ARTIST_ORDER = ["Metallica", "Megadeth", "Slayer", "Anthrax"]
NUMERIC_COLUMNS = ["lastfm_playcount", "lastfm_listeners", "bpm", "track_length_ms"]

ARTIST_COLORS = {
    "Metallica": "#F7C948",
    "Megadeth": "#7FDBFF",
    "Slayer": "#FF6B6B",
    "Anthrax": "#B8F7A1",
}


# Define the full dashboard theme once
CSS = """
<style>
header { visibility: hidden; }

html, body, .stApp {
    background-color: #0b0b0b;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

.block-container { padding-top: 1rem; }

h1, h2, h3, h4 {
    color: #e53935;
    font-weight: 900;
}

hr { border: 1px solid #222; }

label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: white !important;
}

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background-color: #0b0b0b !important;
}

div[data-baseweb="select"],
div[data-baseweb="select"] > div {
    background-color: #111 !important;
    color: white !important;
    border-radius: 10px;
    border: 1px solid #333 !important;
}

div[data-baseweb="select"] input,
ul[role="listbox"],
ul[role="listbox"] li {
    color: white !important;
}

ul[role="listbox"] { background-color: #111 !important; }

span[data-baseweb="tag"] {
    background-color: #e53935 !important;
    color: white !important;
}

[data-testid="stMetric"] {
    background: #111;
    border: 1px solid #ffffff33;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 0 10px rgba(229, 57, 53, 0.2);
}

[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 36px !important;
    font-weight: 900 !important;
}

[data-testid="stDataFrame"] {
    background-color: #0b0b0b !important;
    color: white !important;
}

.section-title {
    font-size: 30px;
    font-weight: 900;
    color: #e53935;
    margin-top: 35px;
    margin-bottom: 20px;
    text-transform: uppercase;
}

.album-card,
.band-panel {
    background: #101010;
    border: 1px solid #2b2b2b;
    border-radius: 18px;
    padding: 18px;
}

.album-card {
    min-height: 310px;
    padding: 24px;
    box-shadow: 0 0 14px rgba(229, 57, 53, 0.18);
}

.band-heading {
    font-size: 26px;
    font-weight: 900;
    color: white;
    text-align: center;
    margin-bottom: 18px;
    border-bottom: 2px solid #e53935;
    padding-bottom: 10px;
}

.track-row {
    display: flex;
    gap: 12px;
    background: #181818;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}

.track-rank {
    background: #e53935;
    color: white;
    font-weight: 900;
    border-radius: 8px;
    padding: 8px 12px;
    min-width: 38px;
    text-align: center;
}

.album-band,
.album-card-title,
.album-value,
.track-title {
    color: white;
    font-weight: 900;
}

.track-title { font-size: 18px; }

.album-date,
.album-label,
.track-meta {
    color: #bdbdbd;
}

.album-bpm,
.album-title,
.album-title-left,
.track-bpm {
    color: #e53935;
    font-weight: 900;
}

.album-band {
    font-size: 28px;
    text-align: center;
}

.album-title {
    font-size: 22px;
    text-align: center;
    min-height: 55px;
}

.album-title-left {
    text-align: left;
    font-size: 22px;
    margin-bottom: 6px;
}

.album-card-title {
    text-align: center;
    font-size: 22px;
    margin: 12px 0 10px;
}

.album-date {
    text-align: center;
    margin-bottom: 20px;
}

.album-divider {
    height: 2px;
    background: #e53935;
    margin: 12px 0 20px;
}

.album-value { font-size: 24px; }
.album-bpm { font-size: 26px; }
</style>
"""


# Load and clean the track data once, then cache it for faster reruns.
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df[NUMERIC_COLUMNS] = df[NUMERIC_COLUMNS].apply(pd.to_numeric, errors="coerce")
    return df[df["album_name"] != "Crazy Sheep"].copy()


# Render a consistent red section title across the dashboard.
def section_title(text: str) -> None:
    st.markdown(
        f'<div class="section-title">⚡ {html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


# Keep selected artists in the classic Big Four display order.
def ordered_selected_artists(selected_artists: list[str]) -> list[str]:
    return [artist for artist in ARTIST_ORDER if artist in selected_artists]


# Build a reusable dark Plotly layout so every chart has the same style.
def dark_layout(title: str, height: int) -> dict:
    return dict(
        plot_bgcolor="#0b0b0b",
        paper_bgcolor="#0b0b0b",
        font=dict(color="white", size=14),
        title=dict(text=title, font=dict(color="white", size=24)),
        xaxis=dict(color="white", gridcolor="#333333", zerolinecolor="#333333"),
        yaxis=dict(color="white", title=""),
        legend=dict(
            title="Artist",
            font=dict(color="white"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=20, r=80, t=70, b=40),
        height=height,
    )


# Draw a horizontal bar chart using the shared artist colors and dark layout.
def horizontal_bar(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_label: str,
    y_label: str = "",
    height: int = 450,
    text_template: str = "%{text:,.0f}",
    hover_data: dict | None = None,
) -> None:
    fig = px.bar(
        data,
        x=x,
        y=y,
        color="artist",
        orientation="h",
        text=x,
        hover_data=hover_data,
        labels={x: x_label, y: y_label},
        color_discrete_map=ARTIST_COLORS,
    )

    fig.update_traces(texttemplate=text_template, textposition="outside")
    fig.update_layout(**dark_layout(title, height))
    fig.update_yaxes(categoryorder="total ascending")

    st.plotly_chart(fig, use_container_width=True)


# Summarize track-level data into album-level statistics used by several sections.
def summarize_albums(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["artist", "album_name", "first_release_date"])
        .agg(
            total_tracks=("track_name", "count"),
            total_playcount=("lastfm_playcount", "sum"),
            total_listeners=("lastfm_listeners", "sum"),
            avg_bpm=("bpm", "mean"),
            avg_track_length_ms=("track_length_ms", "mean"),
        )
        .reset_index()
    )


# Get the top three unique tracks for each artist by Last.fm playcount.
def top_tracks_by_artist(df: pd.DataFrame) -> pd.DataFrame:
    unique_tracks = (
        df.sort_values("lastfm_playcount", ascending=False)
        .drop_duplicates(subset=["artist", "track_name"], keep="first")
    )

    return (
        unique_tracks.sort_values("lastfm_playcount", ascending=False)
        .groupby("artist")
        .head(3)
        .copy()
    )


# Generate a reusable album-style HTML card wrapper.
def card_html(title: str, body: str) -> str:
    return (
        '<div class="album-card">'
        f'<div class="album-band">{html.escape(str(title))}</div>'
        '<div class="album-divider"></div>'
        f"{body}"
        "</div>"
    )


# Render the top track cards for each selected artist.
def render_track_cards(top_tracks: pd.DataFrame, artists: list[str]) -> None:
    if not artists:
        return

    cols = st.columns(len(artists))

    for col, artist in zip(cols, artists):
        artist_tracks = top_tracks[top_tracks["artist"] == artist].reset_index(drop=True)

        with col:
            st.markdown(
                f"""
                <div class="band-panel">
                    <div class="band-heading">{html.escape(artist)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for i, row in artist_tracks.iterrows():
                bpm = "N/A" if pd.isna(row["bpm"]) else f"{row['bpm']:.0f} BPM"
                plays = f"{row['lastfm_playcount']:,.0f}"
                track = html.escape(str(row["track_name"]))

                st.markdown(
                    f"""
                    <div class="track-row">
                        <div class="track-rank">{i + 1}</div>
                        <div>
                            <div class="track-title">{track}</div>
                            <div class="track-meta">Plays: {plays}</div>
                            <div class="track-bpm">BPM: {bpm}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# Render one card per artist for the most popular album.
def render_album_cards(top_albums: pd.DataFrame, artists: list[str]) -> None:
    if not artists:
        return

    cols = st.columns(len(artists))

    for col, artist in zip(cols, artists):
        rows = top_albums[top_albums["artist"] == artist]

        if rows.empty:
            continue

        row = rows.iloc[0]
        album = html.escape(str(row["album_name"]))
        release = html.escape(str(row["first_release_date"]))
        plays = f"{row['total_playcount']:,.0f}"
        bpm = "N/A" if pd.isna(row["avg_bpm"]) else f"{row['avg_bpm']:.1f} BPM"

        with col:
            st.markdown(
                f"""
                <div class="album-card">
                    <div class="album-band">{html.escape(artist)}</div>
                    <div class="album-title">{album}</div>
                    <div class="album-date">Released: {release}</div>
                    <div class="album-divider"></div>
                    <div class="album-label">Total Plays</div>
                    <div class="album-value">{plays}</div>
                    <div class="album-label">Average BPM</div>
                    <div class="album-bpm">{bpm}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# Render side-by-side summary cards for the two selected comparison albums.
def render_comparison_album_cards(compare_stats: pd.DataFrame) -> None:
    if compare_stats.empty:
        return

    cols = st.columns(len(compare_stats))

    for col, (_, row) in zip(cols, compare_stats.iterrows()):
        artist = html.escape(str(row["artist"]))
        album = html.escape(str(row["album_name"]))
        release = html.escape(str(row["first_release_date"]))
        plays = f"{row['total_playcount']:,.0f}"
        listeners = f"{row['total_listeners']:,.0f}"
        bpm = "N/A" if pd.isna(row["avg_bpm"]) else f"{row['avg_bpm']:.1f} BPM"

        with col:
            st.markdown(
                f"""
                <div class="album-card">
                    <div class="album-band">{artist}</div>
                    <div class="album-title">{album}</div>
                    <div class="album-date">Released: {release}</div>
                    <div class="album-divider"></div>
                    <div class="album-label">Total Plays</div>
                    <div class="album-value">{plays}</div>
                    <div class="album-label">Total Listeners</div>
                    <div class="album-value">{listeners}</div>
                    <div class="album-label">Average BPM</div>
                    <div class="album-bpm">{bpm}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# Render detailed per-band cards and charts for listeners, albums, tracks, and BPM.
def render_band_overview_cards(stats: pd.DataFrame, artists: list[str], tracks_df: pd.DataFrame) -> None:
    for artist in artists:
        artist_stats = stats[stats["artist"] == artist].copy()
        artist_tracks = tracks_df[tracks_df["artist"] == artist].copy()

        if artist_stats.empty:
            continue

        total_listeners = artist_stats["total_listeners"].sum()

        most_listened = artist_stats.sort_values("total_playcount", ascending=False).iloc[0]
        least_listened = artist_stats.sort_values("total_playcount", ascending=True).iloc[0]

        bpm_available = artist_stats.dropna(subset=["avg_bpm"])

        fastest_album = (
            bpm_available.sort_values("avg_bpm", ascending=False).iloc[0]
            if not bpm_available.empty
            else None
        )

        slowest_album = (
            bpm_available.sort_values("avg_bpm", ascending=True).iloc[0]
            if not bpm_available.empty
            else None
        )

        # Track-level fastest and slowest songs
        tracks_with_bpm = artist_tracks.dropna(subset=["bpm"]).copy()

        fastest_song = (
            tracks_with_bpm.sort_values("bpm", ascending=False).iloc[0]
            if not tracks_with_bpm.empty
            else None
        )

        slowest_song = (
            tracks_with_bpm.sort_values("bpm", ascending=True).iloc[0]
            if not tracks_with_bpm.empty
            else None
        )

        st.markdown(
            f'<div class="section-title">{html.escape(str(artist))} Overview</div>',
            unsafe_allow_html=True,
        )

        # 2x2 card grid
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            body = (
                '<div class="album-card-title">Total Listeners</div>'
                f'<div class="album-value">{total_listeners:,.0f}</div>'
                '<div class="album-card-title">Studio Albums</div>'
                f'<div class="album-value">{artist_stats["album_name"].nunique()}</div>'
                '<div class="album-card-title">Total Tracks</div>'
                f'<div class="album-value">{artist_stats["total_tracks"].sum():,.0f}</div>'
            )
            st.markdown(card_html(artist, body), unsafe_allow_html=True)

        with row1_col2:
            body = (
                '<div class="album-card-title">Most Listened Album</div>'
                f'<div class="album-title-left">{html.escape(str(most_listened["album_name"]))}</div>'
                f'<div class="album-value">{most_listened["total_playcount"]:,.0f}</div>'
                '<div style="height:18px;"></div>'
                '<div class="album-card-title">Least Listened Album</div>'
                f'<div class="album-title-left">{html.escape(str(least_listened["album_name"]))}</div>'
                f'<div class="album-value">{least_listened["total_playcount"]:,.0f}</div>'
            )
            st.markdown(card_html("Most vs Least Listened", body), unsafe_allow_html=True)

        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            if fastest_album is not None and slowest_album is not None:
                body = (
                    '<div class="album-card-title">Fastest Album</div>'
                    f'<div class="album-title-left">{html.escape(str(fastest_album["album_name"]))}</div>'
                    f'<div class="album-bpm">{fastest_album["avg_bpm"]:.1f} BPM</div>'
                    '<div class="album-label">Plays</div>'
                    f'<div class="album-value">{fastest_album["total_playcount"]:,.0f}</div>'
                    '<div style="height:18px;"></div>'
                    '<div class="album-card-title">Slowest Album</div>'
                    f'<div class="album-title-left">{html.escape(str(slowest_album["album_name"]))}</div>'
                    f'<div class="album-bpm">{slowest_album["avg_bpm"]:.1f} BPM</div>'
                    '<div class="album-label">Plays</div>'
                    f'<div class="album-value">{slowest_album["total_playcount"]:,.0f}</div>'
                )
            else:
                body = (
                    '<div class="album-card-title">BPM Data</div>'
                    '<div class="album-title-left">No album BPM data available</div>'
                )

            st.markdown(card_html("Fastest vs Slowest Albums", body), unsafe_allow_html=True)

        with row2_col2:
            if fastest_song is not None and slowest_song is not None:
                body = (
                    '<div class="album-card-title">Fastest Song</div>'
                    f'<div class="album-title-left">{html.escape(str(fastest_song["track_name"]))}</div>'
                    f'<div class="album-label">{html.escape(str(fastest_song["album_name"]))}</div>'
                    f'<div class="album-bpm">{fastest_song["bpm"]:.1f} BPM</div>'
                    f'<div class="album-label">Plays</div>'
                    f'<div class="album-value">{fastest_song["lastfm_playcount"]:,.0f}</div>'
                    '<div style="height:18px;"></div>'
                    '<div class="album-card-title">Slowest Song</div>'
                    f'<div class="album-title-left">{html.escape(str(slowest_song["track_name"]))}</div>'
                    f'<div class="album-label">{html.escape(str(slowest_song["album_name"]))}</div>'
                    f'<div class="album-bpm">{slowest_song["bpm"]:.1f} BPM</div>'
                    f'<div class="album-label">Plays</div>'
                    f'<div class="album-value">{slowest_song["lastfm_playcount"]:,.0f}</div>'
                )
            else:
                body = (
                    '<div class="album-card-title">Track BPM Data</div>'
                    '<div class="album-title-left">No track BPM data available</div>'
                )

            st.markdown(card_html("Fastest vs Slowest Songs", body), unsafe_allow_html=True)

        artist_bpm_chart = bpm_available.assign(album_label=bpm_available["album_name"])

        horizontal_bar(
            artist_bpm_chart.sort_values("avg_bpm", ascending=True),
            x="avg_bpm",
            y="album_label",
            title=f"{artist}: Albums Sorted by Average BPM",
            x_label="Average BPM",
            y_label="Album",
            height=450,
            text_template="%{text:.1f}",
        )

        horizontal_bar(
            artist_stats.sort_values("total_playcount", ascending=True),
            x="total_playcount",
            y="album_name",
            title=f"{artist}: Albums Sorted by Total Plays",
            x_label="Total Plays",
            y_label="Album",
            height=450,
        )


# Apply the shared CSS theme to the app.
st.markdown(CSS, unsafe_allow_html=True)


# Render the dashboard title and short description.
st.title("Big Four Thrash Metal Dashboard")
st.write(
    "Comparison of Metallica, Megadeth, Slayer and Anthrax using Last.fm, "
    "MusicBrainz and GetSongBPM data."
)


# Load the dataset and prepare artist lists for filters and display order.
df = load_data(DATA_PATH)
artists = sorted(df["artist"].dropna().unique())


# Create sidebar filters and stop gracefully if no artist is selected.
st.sidebar.header("Filters")
selected_artists = st.sidebar.multiselect(
    "Select artists",
    artists,
    default=artists,
)

if not selected_artists:
    st.warning("Select at least one artist to view the dashboard.")
    st.stop()

filtered_df = df[df["artist"].isin(selected_artists)]
selected_ordered = ordered_selected_artists(selected_artists)


# Show high-level dashboard metrics for the currently selected artists.
st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tracks", len(filtered_df))
col2.metric("Total Albums", filtered_df["album_name"].nunique())
col3.metric("Total Playcount", f"{filtered_df['lastfm_playcount'].sum():,.0f}")
col4.metric("Average BPM", f"{filtered_df['bpm'].mean():.1f}")


# Show the top three tracks per selected artist as cards and as a bar chart.
section_title("Top 3 Tracks per Artist")

top_tracks = top_tracks_by_artist(filtered_df)
render_track_cards(top_tracks, selected_ordered)

top_tracks_chart = top_tracks.assign(
    artist_track=lambda x: x["artist"] + " - " + x["track_name"]
)

horizontal_bar(
    top_tracks_chart,
    x="lastfm_playcount",
    y="artist_track",
    title="Top 3 Tracks per Artist by Last.fm Playcount",
    x_label="Total Plays",
    y_label="Track",
    height=600,
    hover_data={
        "artist": True,
        "track_name": True,
        "bpm": True,
        "lastfm_playcount": ":,",
    },
)


# Summarize selected artist data at album level for album sections.
stats = summarize_albums(filtered_df)
top_albums = (
    stats.sort_values("total_playcount", ascending=False)
    .groupby("artist")
    .head(1)
    .copy()
)


# Show the most popular studio album per selected artist.
section_title("Most Popular Studio Album per Artist")
render_album_cards(top_albums, selected_ordered)

top_albums_chart = top_albums.assign(
    artist_album=lambda x: x["artist"] + " - " + x["album_name"]
)

horizontal_bar(
    top_albums_chart,
    x="total_playcount",
    y="artist_album",
    title="Most Popular Studio Album per Artist by Aggregated Track Playcount",
    x_label="Total Plays",
    y_label="Artist - Album",
    height=450,
    hover_data={
        "artist": True,
        "album_name": True,
        "first_release_date": True,
        "avg_bpm": ":.1f",
        "total_tracks": True,
        "total_playcount": ":,",
    },
)


# Let the user choose two albums and compare their playcount, listeners, and BPM.
section_title("Album vs Album Comparison")

col_a, col_b = st.columns(2)

with col_a:
    artist_a = st.selectbox("Select Artist A", artists, index=0)
    albums_a = sorted(df.loc[df["artist"] == artist_a, "album_name"].unique())
    album_a = st.selectbox("Select Album A", albums_a)

with col_b:
    artist_b_index = 1 if len(artists) > 1 else 0
    artist_b = st.selectbox("Select Artist B", artists, index=artist_b_index)
    albums_b = sorted(df.loc[df["artist"] == artist_b, "album_name"].unique())
    album_b = st.selectbox("Select Album B", albums_b)

compare_df = df[
    ((df["artist"] == artist_a) & (df["album_name"] == album_a))
    | ((df["artist"] == artist_b) & (df["album_name"] == album_b))
]

compare_stats = summarize_albums(compare_df).assign(
    artist_album=lambda x: x["artist"] + " - " + x["album_name"]
)

render_comparison_album_cards(compare_stats)

horizontal_bar(
    compare_stats,
    x="avg_bpm",
    y="artist_album",
    title="Average BPM Comparison",
    x_label="Average BPM",
    y_label="Album",
    height=400,
    text_template="%{text:.1f}",
)

horizontal_bar(
    compare_stats,
    x="total_listeners",
    y="artist_album",
    title="Total Listeners Comparison",
    x_label="Total Listeners",
    y_label="Album",
    height=400,
)


# Show a deeper per-band overview using the album-level statistics.
section_title("Band Overview")
render_band_overview_cards(stats, selected_ordered, filtered_df)

import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Movie Rating Analysis",
    page_icon="🎬",
    layout="wide"
)

# White, clean dashboard styling
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    color: #202124;
}
[data-testid="stMetric"] {
    background: #f7f8fa;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
}
h1, h2, h3 {
    color: #202124;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Movie Rating Data Analysis")
st.caption("Big Data Analytics using Java MapReduce, Apache Hive and Python")
# Top 10 Movies from Apache Hive

st.subheader("🏆 Top 10 Highest-Rated Movies (Apache Hive)")

hive_file = "hive_top_movies.csv"

if os.path.exists(hive_file):
    hive_df = pd.read_csv(hive_file)
    st.dataframe(hive_df, use_container_width=True)
else:
    st.warning("Hive results file not found.")

# Dataset paths
data_dir = Path(__file__).parent / "data"
ratings_file = data_dir / "ratings.csv"
movies_file = data_dir / "movies.csv"

@st.cache_data
def load_data():
    ratings = pd.read_csv(ratings_file)
    movies = pd.read_csv(movies_file)
    return ratings, movies

try:
    ratings, movies = load_data()

    ratings["movieId"] = ratings["movieId"].astype(int)
    movies["movieId"] = movies["movieId"].astype(int)

    analysis = ratings.groupby("movieId").agg(
        average_rating=("rating", "mean"),
        total_ratings=("rating", "count")
    ).reset_index()

    analysis = analysis.merge(movies, on="movieId", how="left")
    analysis["average_rating"] = analysis["average_rating"].round(2)

    # Summary metrics
    st.subheader("Dataset Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Ratings", f"{len(ratings):,}")
    c2.metric("Total Movies", f"{len(movies):,}")
    c3.metric("Unique Users", f"{ratings['userId'].nunique():,}")
    c4.metric("Average Rating", f"{ratings['rating'].mean():.2f} / 5")

    st.divider()

    # Movie search
    st.subheader("Explore Movies")
    search = st.text_input("Search for a movie")

    filtered = analysis[
        analysis["title"].str.contains(search, case=False, na=False)
    ] if search else analysis.copy()

    st.dataframe(
        filtered.sort_values("total_ratings", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Most-rated movies
    st.subheader("Most Popular Movies")
    popular = analysis.nlargest(10, "total_ratings").sort_values("total_ratings")

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.barh(popular["title"], popular["total_ratings"])
    ax1.set_xlabel("Number of Ratings")
    ax1.set_ylabel("Movie")
    ax1.set_title("Top 10 Movies by Rating Count")
    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    # Highest-rated movies, requiring at least 50 ratings
    st.subheader("Highest-Rated Movies")
    minimum_ratings = st.slider(
        "Minimum number of ratings",
        min_value=10,
        max_value=100,
        value=50,
        step=10
    )

    top_rated = (
        analysis[analysis["total_ratings"] >= minimum_ratings]
        .nlargest(10, "average_rating")
        .sort_values("average_rating")
    )

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.barh(top_rated["title"], top_rated["average_rating"])
    ax2.set_xlabel("Average Rating out of 5")
    ax2.set_ylabel("Movie")
    ax2.set_xlim(0, 5)
    ax2.set_title("Top 10 Highest-Rated Movies")
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # Rating distribution
    st.subheader("Rating Distribution")
    distribution = ratings["rating"].value_counts().sort_index()

    fig3, ax3 = plt.subplots(figsize=(9, 4))
    ax3.bar(distribution.index.astype(str), distribution.values)
    ax3.set_xlabel("Rating")
    ax3.set_ylabel("Number of Ratings")
    ax3.set_title("Distribution of User Ratings")
    fig3.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    st.divider()
    st.caption(
        "Technology Stack: Java MapReduce | Apache Hive | Python | "
        "Pandas | Matplotlib | Streamlit"
    )

except FileNotFoundError:
    st.error(
        "Dataset files were not found. Please check that ratings.csv "
        "and movies.csv exist in ~/movie-rating-project/data/."
    )
except Exception as error:
    st.error(f"Unable to load the dashboard data: {error}")

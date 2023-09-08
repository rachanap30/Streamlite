import streamlit as st
GitHub repository URL
github_repo_url = 'https://raw.githubusercontent.com/Kiruthika60577/Kiruthika60577/main/'

URLs of your CSV files on GitHub
movies_url = github_repo_url + 'movies.csv'
ratings_url = github_repo_url + 'ratings.csv'

movies_df = pd.read_csv(movies_url)
ratings_df = pd.read_csv(ratings_url)

Sidebar for user input
user_id = st.sidebar.text_input('Enter User ID', '1')
selected_genre = st.sidebar.selectbox('Select Genre', movies_df['genres'].unique())

search_query = st.sidebar.text_input('Search for Movie', '')

filtered_movies = movies_df[movies_df['title'].str.contains(search_query, case=False)]

filtered_movies_with_ratings = filtered_movies.merge(ratings_df, on='movieId')

Button to trigger recommendations
if st.sidebar.button('Get Recommendations'):
    # Filter movies by selected genre
    filtered_movies = filtered_movies[filtered_movies['genres'].str.contains(selected_genre)]

    # Load the recommendation model
    # (Assuming you have already loaded and trained the model)

    # Get movie recommendations for the user (similar to your previous code)

Display the filtered movies with ratings
st.subheader('Filtered Movies with Ratings:')
st.dataframe(filtered_movies_with_ratings[['title', 'rating']])

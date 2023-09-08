# -*- coding: utf-8 -*-
"""Movie_recommendation_r

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VUkUYLsNQsz7qvercM4poJUZhCe_0JQq
"""

import pandas as pd

movies=pd.read_csv('/content/movies.csv')
links=pd.read_csv('/content/links.csv')
ratings=pd.read_csv('/content/ratings.csv')
tags=pd.read_csv('/content/tags.csv')

movies

ratings.shape

movies.shape

movies_ratings = movies.merge(
    ratings,
    how='left',
    on='movieId'
)

movies_ratings.shape

movies_ratings.isna().sum()

movies_ratings = movies_ratings.dropna()

movies_ratings['userId'] = movies_ratings['userId'].astype(int)

movies_ratings.head(1)

"""##3.&nbsp;How should we build a popularity recommender? 📚

###3.1.&nbsp;Higest rated books
Let's the look at the most popular books by average rating
"""

rating_count_df=movies_ratings.groupby('movieId')['rating'].agg(['mean','count']).reset_index()
rating_count_df.nlargest(5,(['mean','count']))

"""movie with the highest mean score"""

highest_rating= rating_count_df.nlargest(1, 'mean')['movieId'].values[0]

highest_rated_movies = movies_ratings['movieId'] == highest_rating
movie_info_columns = ['movieId', 'title', 'genres', 'timestamp']

movies_ratings.loc[highest_rated_movies, movie_info_columns].drop_duplicates('title')

"""###3.2.&nbsp;Most rated books
But are the most highly rated books also the most well read books?
"""

rating_count_df.sort_values(by=['count', 'mean'], ascending=False).head()

"""Book with the most reviews"""

most_rated_movie = rating_count_df.nlargest(1, 'count')['movieId'].values[0]
most_rated_movie_mask = movies_ratings['movieId'] == most_rated_movie

movies_ratings.loc[most_rated_movie_mask, movie_info_columns].drop_duplicates('title')

rating = movies_ratings.groupby('movieId')['rating'].mean()
movie_popularity = movies_ratings['movieId'].value_counts()

# Merge ratings and popularity into a single DataFrame
movie_stats = pd.DataFrame({'mean_rating': rating, 'popularity': movie_popularity})

# Define a popularity threshold (e.g., minimum number of ratings)
popularity_threshold = 100  # Adjust this threshold as needed

# Filter movies above the popularity threshold
popular_movies = movie_stats[movie_stats['popularity'] >= popularity_threshold]

# Sort popular movies by mean rating (you can customize the sorting criteria)
recommended_movies = popular_movies.sort_values(by='mean_rating', ascending=False)

# Merge with movie metadata to get movie details (title, genres, etc.)
recommended_movies = pd.merge(recommended_movies, movies_ratings, left_index=True, right_on='movieId')

# Display the recommended movies
recommended_movies[['movieId', 'title', 'genres']]
recommended_movies.drop_duplicates('title')

# movies_ratings['rating_list'] = ['top_movie' if row['userId'] >= 500 and row['rating'] >= 4.5
#                                  else 'medium' if row['userId'] <= 400 and row['rating'] >= 3.8 else 'not_good' for index, row in movies_ratings.iterrows()]
# movies_ratings

movies_ratings['rating_list'] = ['top_movie' if (row['userId'] >= 500) and (row['rating'] >= 4.5) else 'medium'
                                 if (row['userId'] <= 400) and (row['rating'] >= 3.8) else 'not_good'
                                 for index, row in movies_ratings.iterrows()]

# Now, you can access the 'movieId' values based on the 'rating_list' column
selected_movie_ids = movies_ratings['movieId'][movies_ratings['rating_list'] == 'top_movie'].unique()
selected_movie_ids

grouped_movie = movies_ratings.groupby([movies_ratings['rating_list']]).count()
grouped_movie

def ratings():
  int(input('how many top movies do you want ?'))
  n=input.int()
  print(n);
  return n

def ratings():
    try:
        n = int(input('How many top unique movies do you want? '))
        top_movies = movies_ratings[(movies_ratings['userId'] >= 500) & (movies_ratings['rating'] >= 4.5)]
        unique_top_movies = top_movies.drop_duplicates(subset='movieId')
        # Check if there are at least n unique top movies, and display the top n if available
        if len(unique_top_movies) >= n:
            top_n_unique_movies = unique_top_movies.head(n)
            print(top_n_unique_movies)
        else:
            print("There are not enough unique top-rated movies to display.")
    except ValueError:
        print("Please enter a valid number.")

ratings()

"""##3.&nbsp;User-Item matrix 💻
In order to construct an item-based memory-based recommender system, the initial stage involves creating a user-item matrix. This matrix serves as a fundamental component for storing and examining the interactions between users and items, enabling us to uncover similarities and make predictions. The user-item matrix acts as a representation of the ratings or preferences expressed by users for each item within the system.
"""

movies_ratings

user_movie_matrix = pd.pivot_table(data=movies_ratings,
                                  values='rating',
                                  index='userId',
                                  columns='movieId',
                                  fill_value=0)
user_movie_matrix.head(10)

movie_correlations_matrix = user_movie_matrix.corr()
movie_correlations_matrix

"""####3.1.1.&nbsp;Finding movies similar to the most popular movie - The Lovely Bones
Create a DataFrame of how correlated other movies are to The Lovely Bones
"""

# Find the ISBN for The Lovely Bones
Toy_Story_title_mask = movies_ratings["title"].str.contains('Toy Story (1995)', case=False)
#lovely_bones_author_mask = df["book_author"].str.contains('alice sebold', case=False)
Toy_Story_movie = movies_ratings.loc[Toy_Story_title_mask, "movieId"]

# Select the column, from the above matrix, matching the ISBN of The Lovely Bones
Toy_Story_correlations_df = pd.DataFrame(movie_correlations_matrix[Toy_Story_movie])
Toy_Story_correlations_df.head()

movies_ratings

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Assuming you have a DataFrame called movie_ratings

# Define a function to get movie recommendations based on cosine similarity
def get_movie_recommendations(movie_ratings, movie_id, n):
    # Group by movieId and concatenate genres
    movie_grouped = movies_ratings.groupby('movieId')['genres'].apply(lambda x: ' '.join(x)).reset_index()

    # Initialize TF-IDF Vectorizer
    tfidf_vectorizer = TfidfVectorizer()

    # Fit and transform the TF-IDF vectorizer on the genres
    tfidf_matrix = tfidf_vectorizer.fit_transform(movie_grouped['genres'])

    # Calculate cosine similarity between movies
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Get the index of the input movie
    movie_index = movie_grouped[movie_grouped['movieId'] == movie_id].index[0]

    # Get the cosine similarity scores for all movies
    similarity_scores = cosine_sim[movie_index]

    # Create a DataFrame with movieId and similarity scores
    similar_movies = pd.DataFrame({'movieId': movie_grouped['movieId'], 'similarity': similarity_scores})

    # Sort the DataFrame by similarity scores in descending order
    similar_movies = similar_movies.sort_values(by='similarity', ascending=False)

    # Exclude the input movie from recommendations
    similar_movies = similar_movies[similar_movies['movieId'] != movie_id]

    # Get the top n movie recommendations
    top_n_recommendations = similar_movies.head(n)

    # Merge with movie_metadata to get movie details (title, genres, etc.)
    recommended_movies = pd.merge(top_n_recommendations, movies_ratings, on='movieId')

    return recommended_movies[['movieId', 'title', 'genres']]

# Example usage:
movie_id = 1  # Replace with the desired movie ID
n = 10  # Number of recommendations
recommendations = get_movie_recommendations(movies_ratings, movie_id, n)
recommendations

pip install scikit-surprise

from surprise import Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import NormalPredictor, KNNBasic, KNNWithMeans, SVD

# Create a Surprise Dataset from your DataFrame
reader = Reader(rating_scale=(0.5, 5.0))  # Define the rating scale
data = Dataset.load_from_df(movies_ratings[['userId', 'movieId', 'rating']], reader)

trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
# Create an instance of the recommender algorithm
algo = NormalPredictor()  # Replace with your chosen algorithm
algo.fit(trainset)
predictions = algo.test(testset)
from surprise import accuracy

# Calculate and print RMSE (Root Mean Squared Error)
rmse = accuracy.rmse(predictions)

# Replace 'user_id' with the actual user ID for whom you want recommendations
user_id = 'user_id_here'

# Get a list of all movie IDs
all_movie_ids = movies_ratings['movieId'].unique()

# Generate recommendations for the user
recommendations = []
for movie_id in all_movie_ids:
    prediction = algo.predict(user_id, movie_id)
    recommendations.append((movie_id, prediction.est))

# Sort recommendations by predicted rating in descending order
recommendations.sort(key=lambda x: x[1], reverse=True)

# Display the top N recommended movies
top_n = 10
top_recommendations = recommendations[:top_n]
top_recommendations

movies_ratings.head(1)

data = movies_ratings[['userId', 'movieId', 'rating']]

"""Create a surprise dataset from the DataFrame"""

reader = Reader(rating_scale=(1, 10))
data = Dataset.load_from_df(data, reader)

"""Split the dataset into train and test sets:"""

trainset, testset = train_test_split(data, test_size=0.2, random_state=142)

"""### 2.2.&nbsp;Making a model to test"""

sim_options = {
    'name': 'cosine',
    'user_based': True
}

knn = KNNBasic(sim_options=sim_options)

"""Train the algorithm on the training set:"""

knn.fit(trainset)

"""Make predictions on the test set:"""

predictions = knn.test(testset)

predictions[:5]

"""To enhance readability, let's convert this into a DataFrame, making it more visually appealing and easier to interpret."""

predictions_df = pd.DataFrame(predictions, columns=["raw_user_id", "raw_item_id", "actual_user_rating", "estimated_user_rating", "details"])
predictions_df.head()

"""##### 2.2.2.1.&nbsp;Mean Absolute Error
Mean Absolute Error (MAE) is a simple way to find out how good or bad our recommender system is at guessing the ratings that users give to books. It helps us understand how "off" our guesses are from the real ratings. To calculate MAE, we first find the difference between the actual rating and the estimated rating for each user and book pair. Then, we take the absolute value of these differences (which means we ignore negative signs) and find the average of all these absolute differences.

Here's an example using the first row of the above DataFrame:

1. Actual rating: 10.0, Estimated rating: 8.5
2. Difference: 10.0 - 8.5 = 1.5
3. Absolute difference: |1.5| = 1.5

We repeat this process for all rows and find the average of the absolute differences. That's our Mean Absolute Error! The smaller the MAE, the better our recommender system is at guessing the ratings.
"""

accuracy.mae(predictions)

"""##### 2.2.2.2.&nbsp;Root Mean Square Error
Root Mean Squared Error (RMSE) is another way to find out how good our recommender system is at guessing the ratings users give to books. Like MAE, it helps us understand how "off" our guesses are from the real ratings. To calculate RMSE, we first find the difference between the actual rating and the estimated rating for each user and book pair. Then, we square these differences and find the average of all these squared differences. Finally, we take the square root of this average.

Here's an example using the first row of your dataframe:

1. Actual rating: 10.0, Estimated rating: 8.5
2. Difference: 10.0 - 8.5 = 1.5
3. Squared difference: 1.5 * 1.5 = 2.25

We repeat this process for all rows and find the average of the squared differences, and then take the square root of that average. That's our Root Mean Squared Error! The smaller the RMSE, the better our recommender system is at guessing the ratings. RMSE is more sensitive to large errors than MAE because it squares the differences, so it "punishes" bigger errors more than MAE does.
"""

accuracy.rmse(predictions)

"""##### 2.2.2.3.&nbsp;Fraction of Concordant Pairs
Fraction of Concordant Pairs (FCP) is a way to find out how good our recommender system is at ranking books by comparing pairs of actual ratings and estimated ratings. It helps us understand if our recommender system is correctly ranking books for users. To calculate FCP, we first create pairs of actual ratings and estimated ratings for each user. Then, we count the number of pairs where the relative order of the ratings is the same. This means that if a user rated book A higher than book B, our recommender system should also estimate that the user would rate book A higher than book B. These pairs are called "concordant pairs".

Now, we'll divide the number of concordant pairs by the total number of pairs. That's our Fraction of Concordant Pairs! The higher the FCP, the better our recommender system is at ranking books for users. Unlike MAE and RMSE, which focus on the differences between actual and estimated ratings, FCP focuses on the relative order of the ratings.
"""

accuracy.fcp(predictions)

"""##### **2.2.2.4.&nbsp;The manual approach**

---


In our exploration of supervised machine learning, we examined a histogram of errors and a scatterplot of errors. Here, we will employ a similar approach. We'll begin by analysing a histogram of errors, but we'll replace the scatterplot with a box plot. Given the discrete nature of the data, using a scatterplot results in dots forming lines and overlapping, providing limited insight into density. To gain a better understanding of density and variance, we'll utilise a box plot instead.
"""

predictions_df["difference"] = predictions_df["actual_user_rating"] - predictions_df["estimated_user_rating"]

predictions_df["difference"].hist(bins=30,
                                  figsize=(10, 8));

predictions_df.plot(kind='box',
                    column='estimated_user_rating',
                    by='actual_user_rating',
                    figsize=(10, 8));

sim_options = {
    'name': 'cosine',
    'user_based': True
}

full_train = data.build_full_trainset()
algo = KNNBasic(sim_options=sim_options)
algo.fit(trainset)

testset = trainset.build_anti_testset()
predictions = algo.test(testset)

def get_top_n(predictions, user_id, n=10):

  user_recommendations = []

  # Iterate through each prediction tuple
  for uid, iid, true_r, est, _ in predictions:
    # Check if the user ID matches the target user
    if user_id == uid:
      # Append item_id and estimated_rating to the user_recommendations list
      user_recommendations.append((iid, est))
    else:
      # Skip to the next prediction if user ID doesn't match
      continue

  # Sort the user_recommendations list based on estimated_rating in descending order
  ordered_recommendations = sorted(user_recommendations, key=lambda x: x[1], reverse=True)

  # Get the top n predictions from the ordered_recommendations
  ordered_recommendations_top_n = ordered_recommendations[:n]

  return ordered_recommendations_top_n

user_id = 184
n = 10

top_n = get_top_n(predictions, user_id, n)
top_n

"""Success! 🎉 Now, our final task is to match the ISBNs in the tuples with their

1.   List item
2.   List item

respective book titles and other relevant information.
"""

movies_ratings.head(1)

# Creating a DataFrame from the top_n tuples with columns 'book_isbn' and 'estimated_rating'
tuples_df = pd.DataFrame(top_n, columns=["movieId", "estimated_rating"])

# Creating a copy of the original DataFrame with duplicate 'book_isbn' entries removed
reduced_df = movies_ratings.drop_duplicates(subset='movieId').copy()

# Merging the tuples_df with the reduced_df based on 'book_isbn', retaining only the matching rows
tuples_df_expanded = tuples_df.merge(reduced_df, on="movieId", how='left')

# Selecting specific columns from the merged DataFrame to include in the final result
tuples_df_expanded = tuples_df_expanded[['movieId', 'title', 'genres', 'timestamp']]

# Displaying the expanded DataFrame with relevant book information
tuples_df_expanded
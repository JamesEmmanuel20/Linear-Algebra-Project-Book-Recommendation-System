import os
import pandas as pd
import numpy as np

def prepare_book_crossing_dataset():
    print("Step 1: Checking for data directory and raw files...")
    # Ensure the output directory exists
    os.makedirs('data', exist_ok=True)

    ratings_path = 'BX-Book-Ratings.csv'
    books_path = 'BX_Books.csv'

    if not os.path.exists(ratings_path) or not os.path.exists(books_path):
        raise FileNotFoundError(
            f"Could not find raw CSV files. Ensure '{ratings_path}' and '{books_path}' "
            "are placed in the root directory."
        )

    print("Step 2: Reading raw dataset files...")
    # Book-Crossing CSV files use semicolon delimiters and latin-1 encoding
    ratings = pd.read_csv(ratings_path, sep=';', encoding='latin-1', on_bad_lines='skip')
    books = pd.read_csv(books_path, sep=';', encoding='latin-1', on_bad_lines='skip', low_memory=False)

    print("Step 3: Filtering explicit ratings (1-10) and scaling to 1-5...")
    # Filter out 0 (implicit interactions/unrated books)
    ratings = ratings[ratings['Book-Rating'] > 0]

    # Convert 1-10 rating scale to 1-5 scale for clearer matrix representation
    ratings['Book-Rating'] = (ratings['Book-Rating'] / 2).round().astype(int)

    print("Step 4: Merging ratings with book titles via ISBN...")
    # Merge on ISBN to associate numerical ratings with actual book names
    df = ratings.merge(books[['ISBN', 'Book-Title']], on='ISBN')

    # Clean title names (remove non-alphanumeric chars and replace spaces with underscores)
    df['Book-Title'] = df['Book-Title'].str.replace(r'[^\w\s]', '', regex=True).str.strip().str.replace(' ', '_')

    print("Step 5: Filtering active users and popular books to ensure high vector density...")
    # Select books with at least 25 ratings
    book_counts = df['Book-Title'].value_counts()
    popular_books = book_counts[book_counts >= 25].index

    # Select users who have rated at least 10 books
    user_counts = df['User-ID'].value_counts()
    active_users = user_counts[user_counts >= 10].index

    filtered_df = df[(df['Book-Title'].isin(popular_books)) & (df['User-ID'].isin(active_users))]

    print("Step 6: Pivoting into User-Item Matrix...")
    # Rows = Users, Columns = Books, Values = Ratings (1-5)
    pivot_table = filtered_df.pivot_table(index='User-ID', columns='Book-Title', values='Book-Rating')

    print("Step 7: Slicing the dense 40 Users x 15 Books sub-matrix...")
    # Find the top 15 books with the most non-null ratings in this subset
    top_15_books = pivot_table.notna().sum(axis=0).nlargest(15).index
    sub_pivot = pivot_table[top_15_books]

    # Find the top 40 users with the most non-null ratings across these 15 books
    top_40_users = sub_pivot.notna().sum(axis=1).nlargest(40).index
    dense_matrix = sub_pivot.loc[top_40_users]

    print("Step 8: Imputing missing ratings with column means (Book Average Vector)...")
    # Fill missing entries (NaNs) with the mean rating of that column (average book score)
    dense_matrix = dense_matrix.apply(lambda col: col.fillna(round(col.mean(), 1)))

    # Prefix user IDs for clean display on the dashboard (e.g., User_276729)
    dense_matrix.index = [f"User_{uid}" for uid in dense_matrix.index]

    output_file = 'data/book_ratings.csv'
    dense_matrix.to_csv(output_file)
    print(f"✅ Success! Created {output_file} with matrix shape {dense_matrix.shape} (40 Users x 15 Books).")

if __name__ == "__main__":
    prepare_book_crossing_dataset()
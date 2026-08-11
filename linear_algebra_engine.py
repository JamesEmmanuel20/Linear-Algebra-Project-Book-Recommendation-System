import pandas as pd
import numpy as np


class BookRecommenderEngine:
    """
    Linear Algebra Engine for User-Item Matrix Recommendation.

    Mathematical Model:
    - Matrix R in R^(m x n), where m = number of users
      and n = number of books.
    - Each row vector u_i in R^n represents a user's
      preference across all books.
    - Each column vector v_j in R^m represents a book's
      ratings across all users.
    """

    def __init__(self, csv_path: str):
        # Read user-item matrix from CSV
        self.df = pd.read_csv(csv_path, index_col=0)

        self.users = list(self.df.index)
        self.books = list(self.df.columns)

        # Convert DataFrame to NumPy matrix R
        self.R = self.df.to_numpy(dtype=float)

        self.num_users, self.num_books = self.R.shape

    def get_user_vector(self, user_name: str) -> np.ndarray:
        """
        Extract the row vector u_i for the target user.
        """

        if user_name not in self.users:
            raise ValueError(
                f"User '{user_name}' not found in the dataset matrix."
            )

        idx = self.users.index(user_name)

        return self.R[idx, :]

    def compute_euclidean_distance(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """
        Computes Euclidean distance between two user vectors.

        d(u, v) = ||u - v||_2
        """

        diff = vec1 - vec2

        return float(
            np.sqrt(np.dot(diff, diff))
        )

    def compute_cosine_similarity(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """
        Computes cosine similarity between two user vectors.

        cos(theta) =
        (u . v) / (||u||_2 * ||v||_2)
        """

        dot_product = np.dot(vec1, vec2)

        norm_u = np.linalg.norm(vec1)
        norm_v = np.linalg.norm(vec2)

        if norm_u == 0 or norm_v == 0:
            return 0.0

        return float(
            dot_product / (norm_u * norm_v)
        )

    def find_most_similar_user(
        self,
        target_user: str,
        metric: str = "euclidean"
    ):
        """
        Finds the user whose preference vector is most
        similar to the target user's vector.

        Euclidean:
            Smaller distance = more similar

        Cosine:
            Larger similarity = more similar
        """

        target_vec = self.get_user_vector(target_user)

        if metric == "euclidean":
            best_score = float("inf")
        elif metric == "cosine":
            best_score = -1.0
        else:
            raise ValueError(
                "Unknown metric. Use 'euclidean' or 'cosine'."
            )

        most_similar_user = None

        for i, user in enumerate(self.users):

            # Do not compare the user with themselves
            if user == target_user:
                continue

            current_vec = self.R[i, :]

            if metric == "euclidean":

                score = self.compute_euclidean_distance(
                    target_vec,
                    current_vec
                )

                if score < best_score:
                    best_score = score
                    most_similar_user = user

            else:

                score = self.compute_cosine_similarity(
                    target_vec,
                    current_vec
                )

                if score > best_score:
                    best_score = score
                    most_similar_user = user

        return most_similar_user, round(best_score, 4)

    def generate_recommendations(
        self,
        target_user: str,
        metric: str = "euclidean",
        threshold: float = 3.5
    ):
        """
        Generates book recommendations by comparing the
        target user's ratings with their most similar user.

        A book is recommended when:

        1. The similar user rated the book highly
           (>= threshold).

        2. The similar user rated the book higher than
           the target user.

        Recommendations are ranked by rating difference.
        """

        # Find the most similar user
        similar_user, distance_score = (
            self.find_most_similar_user(
                target_user,
                metric=metric
            )
        )

        # Get both user vectors
        target_vec = self.get_user_vector(target_user)
        similar_vec = self.get_user_vector(similar_user)

        recommendations = []

        # Compare every book
        for j in range(self.num_books):

            target_rating = target_vec[j]
            similar_rating = similar_vec[j]

            # Recommend when the similar user:
            # 1. rated the book highly
            # 2. rated it higher than the target user
            if (
                similar_rating >= threshold
                and similar_rating > target_rating
            ):

                recommendations.append({
                    "book": self.books[j],
                    "similar_user_rating": float(
                        similar_rating
                    ),
                    "target_user_rating": float(
                        target_rating
                    ),
                    "rating_difference": round(
                        float(
                            similar_rating - target_rating
                        ),
                        2
                    )
                })

        # Strongest recommendations first
        recommendations.sort(
            key=lambda item: item["rating_difference"],
            reverse=True
        )

        # Return a maximum of five recommendations
        recommendations = recommendations[:5]

        return {
            "target_user": target_user,
            "most_similar_user": similar_user,
            "metric_used": metric,
            "score": distance_score,
            "recommendations": recommendations
        }

    def compute_item_averages(self) -> dict:
        """
        Computes the average rating of every book.

        This represents the column mean vector of matrix R.
        """

        column_means = np.mean(
            self.R,
            axis=0
        )

        return dict(
            zip(
                self.books,
                np.round(column_means, 2)
            )
        )


# =========================================================
# TERMINAL VERIFICATION
# =========================================================

if __name__ == "__main__":

    try:

        engine = BookRecommenderEngine(
            "data/book_ratings.csv"
        )

        print(
            "Matrix Loaded Successfully! "
            f"Dimensions: {engine.R.shape} (m x n)"
        )

        sample_user = engine.users[0]

        print(
            f"\nTesting recommendations for: "
            f"{sample_user}"
        )

        # Euclidean test
        euc_result = engine.generate_recommendations(
            sample_user,
            metric="euclidean"
        )

        print(
            "\nEuclidean Distance Result:"
        )

        print(euc_result)

        # Cosine test
        cos_result = engine.generate_recommendations(
            sample_user,
            metric="cosine"
        )

        print(
            "\nCosine Similarity Result:"
        )

        print(cos_result)

        # Average ratings test
        averages = engine.compute_item_averages()

        print(
            "\nColumn Mean Vector "
            "(first 3 books):"
        )

        print(
            list(averages.items())[:3]
        )

    except FileNotFoundError:

        print(
            "Run 'python preprocess.py' first "
            "to generate 'data/book_ratings.csv'."
        )
import pandas as pd
import numpy as np


class BookRecommenderEngine:
    """
    Linear Algebra Engine for User-Item Matrix Recommendation.
    
    Mathematical Model:
    - Matrix R in R^(m x n) where m = number of users, n = number of items (books).
    - Each row vector u_i in R^n represents User i's preference across all books.
    - Each column vector v_j in R^m represents Book j's ratings across all users.
    """

    def __init__(self, csv_path: str):
        # Read user-item matrix from CSV
        self.df = pd.read_csv(csv_path, index_col=0)
        self.users = list(self.df.index)
        self.books = list(self.df.columns)
        
        # Convert DataFrame to a 2D NumPy array: Matrix R in R^(m x n)
        self.R = self.df.to_numpy(dtype=float)
        self.num_users, self.num_books = self.R.shape

    def get_user_vector(self, user_name: str) -> np.ndarray:
        """
        Extracts row vector u_i in R^n for a given user.
        """
        if user_name not in self.users:
            raise ValueError(f"User '{user_name}' not found in the dataset matrix.")
        idx = self.users.index(user_name)
        return self.R[idx, :]

    def compute_euclidean_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Linear Algebra Concept: L2 Norm of Difference Vector.
        
        Formula:
            d(u, v) = ||u - v||_2 = sqrt( sum_{k=1}^n (u_k - v_k)^2 )
            
        Equivalently via inner product:
            d(u, v) = sqrt( (u - v) . (u - v) )
        """
        diff = vec1 - vec2
        # np.dot(diff, diff) computes the inner product of the difference vector with itself
        return float(np.sqrt(np.dot(diff, diff)))

    def compute_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Linear Algebra Concept: Normalized Inner Product (Cosine of Angle Theta).
        
        Formula:
            cos(theta) = (u . v) / (||u||_2 * ||v||_2)
            
        Measures orientation alignment independent of vector magnitude.
        """
        dot_product = np.dot(vec1, vec2)
        norm_u = np.linalg.norm(vec1)  # L2 norm of vec1
        norm_v = np.linalg.norm(vec2)  # L2 norm of vec2

        if norm_u == 0 or norm_v == 0:
            return 0.0  # Handle zero vectors to prevent division by zero

        return float(dot_product / (norm_u * norm_v))

    def find_most_similar_user(self, target_user: str, metric: str = 'euclidean'):
        """
        Searches the matrix for the nearest neighbor vector v_k to target vector u.
        
         If metric == 'euclidean': Minimizes L2 distance ||u - v||_2
         If metric == 'cosine': Maximizes cos(theta) = (u . v) / (||u|| * ||v||)
        """
        target_vec = self.get_user_vector(target_user)

        best_score = float('inf') if metric == 'euclidean' else -1.0
        most_similar_user = None

        for i, user in enumerate(self.users):
            if user == target_user:
                continue  # Skip self-comparison

            current_vec = self.R[i, :]

            if metric == 'euclidean':
                score = self.compute_euclidean_distance(target_vec, current_vec)
                if score < best_score:
                    best_score = score
                    most_similar_user = user
            elif metric == 'cosine':
                score = self.compute_cosine_similarity(target_vec, current_vec)
                if score > best_score:
                    best_score = score
                    most_similar_user = user
            else:
                raise ValueError(f"Unknown metric '{metric}'. Use 'euclidean' or 'cosine'.")

        return most_similar_user, round(best_score, 4)

    def generate_recommendations(self, target_user: str, metric: str = 'euclidean', threshold: float = 3.5):
        """
        Generates recommendations by comparing the target user's vector u
        with their nearest neighbor vector v in the matrix space R^n.
        """
        similar_user, distance_score = self.find_most_similar_user(target_user, metric=metric)

        target_vec = self.get_user_vector(target_user)
        similar_vec = self.get_user_vector(similar_user)

        recommendations = []
        for j in range(self.num_books):
            # Target rated low/unseen (< threshold) BUT similar user rated high (>= threshold)
            if target_vec[j] < threshold and similar_vec[j] >= threshold:
                recommendations.append({
                    "book": self.books[j],
                    "similar_user_rating": float(similar_vec[j]),
                    "target_user_rating": float(target_vec[j])
                })

        return {
            "target_user": target_user,
            "most_similar_user": similar_user,
            "metric_used": metric,
            "score": distance_score,
            "recommendations": recommendations
        }

    def compute_item_averages(self) -> dict:
        """
        Linear Algebra Concept: Column Mean Transformation.
        
        Computes mean vector m in R^n across all user rows (axis 0 of Matrix R).
        Returns a dictionary mapping each book column to its mean rating.
        """
        # Linear algebra column mean: (1/m) * sum_{i=1}^m R_{i, j}
        column_means = np.mean(self.R, axis=0)
        return dict(zip(self.books, np.round(column_means, 2)))


# Terminal Verification Block
if __name__ == "__main__":
    try:
        engine = BookRecommenderEngine("data/book_ratings.csv")
        print(f"Matrix Loaded Successfully! Dimensions: {engine.R.shape} (m x n)")
        
        sample_user = engine.users[0]
        print(f"\nTesting recommendations for vector: {sample_user}")
        
        euc_result = engine.generate_recommendations(sample_user, metric='euclidean')
        print("Euclidean Distance Result:", euc_result)
        
        cos_result = engine.generate_recommendations(sample_user, metric='cosine')
        print("Cosine Similarity Result:", cos_result)

        averages = engine.compute_item_averages()
        print("\nColumn Mean Vector (Item Averages):", list(averages.items())[:3])
    except FileNotFoundError:
        print("Run 'python preprocess.py' first to generate 'data/book_ratings.csv'.")
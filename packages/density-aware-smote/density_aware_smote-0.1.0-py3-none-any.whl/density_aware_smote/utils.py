import pandas as pd
from sklearn.model_selection import train_test_split

def load_dataset(path):
    """Load dataset from CSV file."""
    return pd.read_csv(path)

def train_test_split_data(X, y, test_size=0.2, random_state=42):
    """Split dataset into train/test sets."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

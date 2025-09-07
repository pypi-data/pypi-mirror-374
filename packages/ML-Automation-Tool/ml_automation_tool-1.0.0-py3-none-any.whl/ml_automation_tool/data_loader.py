import pandas as pd
from sklearn.model_selection import train_test_split

def load_data(file_path, target_column, test_size=0.2, random_state=42):
    df = pd.read_csv(file_path)
    df = df.dropna()  # simple cleaning
    X = df.drop(columns=[target_column])
    y = df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                        test_size=test_size, 
                                                        random_state=random_state)
    return X_train, X_test, y_train, y_test

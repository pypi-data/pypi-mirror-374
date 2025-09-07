from sklearn.metrics import accuracy_score, f1_score

def evaluate_models(models, X_test, y_test):
    results = {}
    for name, model in models.items():
        y_pred = model.predict(X_test)
        results[name] = {
            "accuracy": accuracy_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred, average="weighted")
        }
    best_model_name = max(results, key=lambda x: results[x]["accuracy"])
    return results, best_model_name

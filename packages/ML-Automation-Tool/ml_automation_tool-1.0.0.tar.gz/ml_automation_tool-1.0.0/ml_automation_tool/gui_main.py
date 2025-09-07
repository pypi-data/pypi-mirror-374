import PySimpleGUI as sg
from ml_automation_tool.data_loader import load_data
from ml_automation_tool.models import train_models
from ml_automation_tool.evaluator import evaluate_models
from ml_automation_tool.utils import save_model

def main():
    # GUI Layout
    layout = [
        [sg.Text("Machine Learning Automation Tool", font=("Helvetica", 16))],
        [sg.Text("CSV File Path:"), sg.Input(key="-FILE-"), sg.FileBrowse(file_types=(("CSV Files", "*.csv"),))],
        [sg.Text("Target Column:"), sg.Input(key="-TARGET-")],
        [sg.Button("Run"), sg.Button("Exit")],
        [sg.Output(size=(80, 20))]  # Output box to display results
    ]

    window = sg.Window("ML Automation Tool", layout)

    # Event Loop
    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        if event == "Run":
            file_path = values["-FILE-"]
            target_column = values["-TARGET-"]
            
            if not file_path or not target_column:
                print("Please provide CSV file and target column!")
                continue
            
            try:
                # Load, train, and evaluate
                X_train, X_test, y_train, y_test = load_data(file_path, target_column)
                models = train_models(X_train, y_train)
                results, best_model_name = evaluate_models(models, X_test, y_test)
                
                print("\nEvaluation Results:")
                for name, metrics in results.items():
                    print(f"{name}: Accuracy={metrics['accuracy']:.2f}, F1 Score={metrics['f1_score']:.2f}")
                
                best_model = models[best_model_name]
                save_model(best_model)
                print(f"\nBest model '{best_model_name}' saved as 'best_model.pkl'\n")
            except Exception as e:
                print(f"Error: {e}")

    window.close()

if __name__ == "__main__":
    main()

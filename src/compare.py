import json
from sklearn.metrics import accuracy_score, f1_score, classification_report

# Load data
with open("knn_classification_results.json") as f:
    predictions = json.load(f)

with open("ground_truth.json") as f:
    ground_truth = json.load(f)

# Build lookup: (GlobalId, graph_version) -> true label
gt_lookup = {}
for item in ground_truth:
    key = (item["GlobalId"], item["graph_version"])
    # ground truth uses "label" but one entry has "predicted" instead
    label = item.get("label")
    gt_lookup[key] = label

# Match predictions to ground truth
y_true = []
y_pred = []
for item in predictions:
    key = (item["GlobalId"], item["graph_version"])
    if key in gt_lookup:
        y_true.append(gt_lookup[key].lower())
        y_pred.append(item["predicted"].lower())    

# Results
print(f"Matched samples: {len(y_true)}")
print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
print(f"F1 (macro): {f1_score(y_true, y_pred, average='macro', zero_division=0):.4f}")
print(f"F1 (weighted): {f1_score(y_true, y_pred, average='weighted', zero_division=0):.4f}")
print("\nClassification Report:")
print(classification_report(y_true, y_pred, zero_division=0))
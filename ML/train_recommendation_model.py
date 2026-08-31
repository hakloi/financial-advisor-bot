#!/usr/bin/env python3
import csv
from pathlib import Path

from backend.finance.recommendations import load_recommendation_model, save_recommendation_model


def load_transactions(csv_path: Path):
    rows = []
    with csv_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            income = float(row.get("income") or 0.0)
            expense = float(row.get("expense") or 0.0)
            if income > 0:
                rows.append({"kind": "income", "amount": income, "category": "Salary"})
            if expense > 0:
                rows.append({
                    "kind": "expense",
                    "amount": expense,
                    "category": row.get("category") or "Other",
                })
    return rows


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    csv_path = root / "finance_3_months.csv"
    model = load_recommendation_model(root / "recommendation_model.json")
    # Rebuild model using the bundled CSV so it reflects available historical data.
    data = load_transactions(csv_path)
    from backend.finance.recommendations import train_recommendation_model

    trained = train_recommendation_model(data)
    save_recommendation_model(trained, root / "recommendation_model.json")
    print(f"Trained recommendation model saved to {root / 'recommendation_model.json'}")
    print(trained)

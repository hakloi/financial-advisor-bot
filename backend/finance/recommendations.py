import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
ML_DIR = ROOT_DIR / "ML"
MODEL_PATH = ML_DIR / "recommendation_model.json"

DEFAULT_MODEL = {
    "category_spending": {
        "Food": 0.32,
        "Housing": 0.25,
        "Transport": 0.12,
        "Entertainment": 0.1,
        "Shopping": 0.08,
        "Health": 0.06,
        "Other": 0.07,
    },
    "savings_target": 0.2,
    "risk_profile": {
        "low": {"equity": 0.2, "bonds": 0.5, "cash": 0.3},
        "medium": {"equity": 0.45, "bonds": 0.35, "cash": 0.2},
        "high": {"equity": 0.7, "bonds": 0.2, "cash": 0.1},
    },
}


def _normalize_category(value):
    raw = (value or "").strip()
    if not raw:
        return "Other"
    aliases = {
        "salary": "Salary",
        "freelance": "Freelance",
        "business": "Business",
        "gift": "Gift",
        "interest": "Interest",
        "housing": "Housing",
        "food": "Food",
        "transport": "Transport",
        "shopping": "Shopping",
        "health": "Health",
        "entertainment": "Entertainment",
        "utilities": "Utilities",
        "travel": "Travel",
        "other": "Other",
    }
    key = raw.lower()
    return aliases.get(key, raw.title())


def _load_csv_transactions(csv_path: Path):
    if not csv_path.exists():
        return []
    rows = []
    with csv_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            amount = float(row.get("income") or 0.0)
            kind = "income" if amount > 0 else "expense"
            if kind == "income":
                rows.append({
                    "kind": "income",
                    "amount": amount,
                    "category": "Salary",
                })
            else:
                rows.append({
                    "kind": "expense",
                    "amount": float(row.get("expense") or 0.0),
                    "category": row.get("category") or "Other",
                })
    return rows


def train_recommendation_model(transactions):
    expense_by_category = defaultdict(float)
    income_total = 0.0
    expense_total = 0.0

    for item in transactions:
        if not item:
            continue
        kind = str(item.get("kind", "")).lower()
        amount = float(item.get("amount") or 0.0)
        if amount <= 0:
            continue
        if kind == "income":
            income_total += amount
        elif kind == "expense":
            expense_total += amount
            category = _normalize_category(item.get("category") or "Other")
            expense_by_category[category] += amount

    if not expense_by_category and expense_total <= 0:
        return DEFAULT_MODEL.copy()

    total_expense = max(expense_total, 1.0)
    spending = {
        category: round(value / total_expense, 4)
        for category, value in sorted(expense_by_category.items(), key=lambda pair: pair[1], reverse=True)
    }

    if not spending:
        spending = DEFAULT_MODEL["category_spending"].copy()

    savings_target = 0.18
    if income_total > 0:
        savings_target = max(0.05, min(0.35, round((income_total - expense_total) / income_total, 4)))

    model = {
        "category_spending": spending,
        "savings_target": round(savings_target, 4),
        "risk_profile": {
            "low": {"equity": 0.2, "bonds": 0.5, "cash": 0.3},
            "medium": {"equity": 0.45, "bonds": 0.35, "cash": 0.2},
            "high": {"equity": 0.7, "bonds": 0.2, "cash": 0.1},
        },
    }
    return model


def save_recommendation_model(model, path: Path = MODEL_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(model, handle, ensure_ascii=False, indent=2)
    return str(path)


def load_recommendation_model(path: Path = MODEL_PATH):
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            pass

    csv_path = ML_DIR / "finance_3_months.csv"
    model = train_recommendation_model(_load_csv_transactions(csv_path))
    save_recommendation_model(model, path)
    return model


def ensure_model_exists(path: Path = MODEL_PATH):
    if not path.exists():
        return load_recommendation_model(path)
    return load_recommendation_model(path)


def build_personalized_recommendations(profile, transactions, model=None):
    model = model or load_recommendation_model()

    risk_level = (profile or {}).get("risk_level") or "medium"
    current_savings = float((profile or {}).get("current_savings") or 0.0)
    investment_horizon = str((profile or {}).get("investment_horizon") or "medium").lower()

    income_total = 0.0
    expense_total = 0.0
    category_totals = defaultdict(float)

    for item in transactions or []:
        amount = float(item.get("amount") or 0.0)
        if amount <= 0:
            continue
        if str(item.get("kind", "")).lower() == "income":
            income_total += amount
        else:
            expense_total += amount
            category = _normalize_category(item.get("category") or "Other")
            category_totals[category] += amount

    monthly_balance = income_total - expense_total
    savings_rate = 0.0 if income_total <= 0 else monthly_balance / income_total
    target_rate = float(model.get("savings_target", 0.2))

    recommendations = []

    if savings_rate < target_rate:
        recommendations.append({
            "title": "Increase your savings buffer",
            "detail": f"Your current savings rate is {savings_rate:.1%}. Aim for at least {target_rate:.1%} to build a more resilient cash buffer.",
            "priority": "high",
        })

    if category_totals:
        top_category, top_amount = max(category_totals.items(), key=lambda pair: pair[1])
        baseline = float((model.get("category_spending") or {}).get(top_category, 0.15))
        top_share = top_amount / max(expense_total, 1.0)

        if top_share > baseline + 0.05:
            recommendations.append({
                "title": f"Review {top_category} spending",
                "detail": f"{top_category} already takes {top_share:.1%} of your expenses. A moderate reduction here can free up cash without harming essentials.",
                "priority": "medium",
            })

    if risk_level not in {"low", "medium", "high"}:
        risk_level = "medium"

    horizon_hint = "short-term buffer" if "1 year" in investment_horizon or "short" in investment_horizon else "long-term growth"
    risk_profile = (model.get("risk_profile") or {}).get(risk_level, {"equity": 0.45, "bonds": 0.35, "cash": 0.2})
    recommendations.append({
        "title": "Match your portfolio to your risk profile",
        "detail": f"For a {risk_level} risk profile and {horizon_hint}, a portfolio split of {risk_profile.get('equity', 0.45):.0%} equities, {risk_profile.get('bonds', 0.35):.0%} bonds and {risk_profile.get('cash', 0.2):.0%} cash fits your profile well.",
        "priority": "medium",
    })

    if current_savings <= 0:
        recommendations.append({
            "title": "Start a monthly emergency reserve",
            "detail": "Set aside a fixed amount every paycheck to protect your financial stability before investing more heavily.",
            "priority": "high",
        })

    if not recommendations:
        recommendations.append({
            "title": "Keep a steady cash flow",
            "detail": "Your habits are balanced. Continue tracking spending and keep a monthly surplus to accelerate your goals.",
            "priority": "low",
        })

    return recommendations[:4]

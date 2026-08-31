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


def build_personalized_recommendations(profile, transactions, model=None, lang="en"):
    model = model or load_recommendation_model()
    lang = (lang or "en").lower()

    risk_level = (profile or {}).get("risk_level") or "medium"
    current_savings = float((profile or {}).get("current_savings") or 0.0)
    investment_horizon = str((profile or {}).get("investment_horizon") or "medium").lower()
    category_labels = {
        "en": {
            "Salary": "Salary",
            "Freelance": "Freelance",
            "Business": "Business",
            "Gift": "Gift",
            "Interest": "Interest",
            "Housing": "Housing",
            "Food": "Food",
            "Transport": "Transport",
            "Shopping": "Shopping",
            "Health": "Health",
            "Entertainment": "Entertainment",
            "Utilities": "Utilities",
            "Travel": "Travel",
            "Other": "Other",
        },
        "ru": {
            "Salary": "Зарплата",
            "Freelance": "Фриланс",
            "Business": "Бизнес",
            "Gift": "Подарок",
            "Interest": "Проценты",
            "Housing": "Жильё",
            "Food": "Еда",
            "Transport": "Транспорт",
            "Shopping": "Покупки",
            "Health": "Здоровье",
            "Entertainment": "Развлечения",
            "Utilities": "Коммунальные",
            "Travel": "Путешествия",
            "Other": "Другое",
        },
    }[lang]

    income_total = 0.0
    expense_total = 0.0
    category_totals = defaultdict(float)
    income_by_category = defaultdict(float)

    for item in transactions or []:
        amount = float(item.get("amount") or 0.0)
        if amount <= 0:
            continue
        kind = str(item.get("kind", "")).lower()
        if kind == "income":
            income_total += amount
            category = _normalize_category(item.get("category") or "Salary")
            income_by_category[category] += amount
        else:
            expense_total += amount
            category = _normalize_category(item.get("category") or "Other")
            category_totals[category] += amount

    monthly_balance = income_total - expense_total
    savings_rate = 0.0 if income_total <= 0 else monthly_balance / income_total
    target_rate = float(model.get("savings_target", 0.2))

    risk_label = risk_level if risk_level in {"low", "medium", "high"} else "medium"
    risk_label_text = {
        "en": {"low": "low", "medium": "medium", "high": "high"},
        "ru": {"low": "низкий", "medium": "средний", "high": "высокий"},
    }[lang].get(risk_label, risk_label)
    horizon_hint = "short-term buffer" if "1 year" in investment_horizon or "short" in investment_horizon else "long-term growth"
    horizon_hint_ru = "краткосрочный резерв" if "1 year" in investment_horizon or "short" in investment_horizon else "долгосрочный рост"

    recommendations = []

    if category_totals:
        top_category, top_amount = max(category_totals.items(), key=lambda pair: pair[1])
        baseline = float((model.get("category_spending") or {}).get(top_category, 0.15))
        top_share = top_amount / max(expense_total, 1.0)
        share_delta = top_share - baseline

        localized_category = category_labels.get(top_category, top_category)
        if lang == "ru":
            recommendations.append({
                "title": f"Трата {localized_category} — самая большая",
                "detail": f"В этом периоде на {localized_category.lower()} потрачено {top_amount:,.0f} ₽, что составляет {top_share:.1%} от всех расходов. Норматив модели для этой категории — {baseline:.1%}.",
                "priority": "high",
            })
        else:
            recommendations.append({
                "title": f"{localized_category} is your biggest expense",
                "detail": f"You spent {top_amount:,.0f} ₽ on {localized_category}, which is {top_share:.1%} of all expenses. The model baseline for this category is {baseline:.1%}.",
                "priority": "high",
            })

        if share_delta > 0.05:
            localized_category = category_labels.get(top_category, top_category)
            if lang == "ru":
                recommendations.append({
                    "title": f"Сократите {localized_category.lower()} до нормы",
                    "detail": f"Траты по {localized_category.lower()} превышают модельный ориентир на {share_delta:.1%}. Снижение на 5–10% здесь быстро освободит деньги для накоплений.",
                    "priority": "medium",
                })
            else:
                recommendations.append({
                    "title": f"Cut {localized_category} to the model norm",
                    "detail": f"Spending on {localized_category} is {share_delta:.1%} above the model benchmark. Reducing it by 5–10% would quickly free up cash for savings.",
                    "priority": "medium",
                })

    if income_total > 0 and expense_total > 0:
        expense_ratio = expense_total / income_total
        if lang == "ru":
            recommendations.append({
                "title": "Соотношение доходов и расходов",
                "detail": f"Расходы составляют {expense_ratio:.1%} от доходов. Оставшийся баланс — {monthly_balance:,.0f} ₽. Чтобы удерживать устойчивый сценарий, сохраняйте минимум {target_rate:.1%} от дохода.",
                "priority": "medium",
            })
        else:
            recommendations.append({
                "title": "Income-to-expense balance",
                "detail": f"Expenses are {expense_ratio:.1%} of income, with a net balance of {monthly_balance:,.0f} ₽. To keep the scenario healthy, aim to save at least {target_rate:.1%} of income.",
                "priority": "medium",
            })

    if savings_rate < target_rate:
        if lang == "ru":
            recommendations.append({
                "title": "Увеличьте резерв накоплений",
                "detail": f"Ваш текущий уровень сбережений — {savings_rate:.1%}. Цель модели — {target_rate:.1%}. Сохранение даже 5–10% от дохода даст заметный запас на форс-мажор.",
                "priority": "high",
            })
        else:
            recommendations.append({
                "title": "Increase your savings buffer",
                "detail": f"Your current savings rate is {savings_rate:.1%}. The model target is {target_rate:.1%}. Saving even 5–10% of income would significantly improve your cushion.",
                "priority": "high",
            })

    if income_by_category:
        top_income_category, top_income_amount = max(income_by_category.items(), key=lambda pair: pair[1])
        if lang == "ru":
            recommendations.append({
                "title": "Основной источник дохода",
                "detail": f"Больше всего денег приходит из категории {top_income_category}: {top_income_amount:,.0f} ₽. Стабильность дохода важнее, чем быстрый рост расходов.",
                "priority": "low",
            })
        else:
            recommendations.append({
                "title": "Main income source",
                "detail": f"Most of your income comes from {top_income_category}: {top_income_amount:,.0f} ₽. Keeping this stream stable is a stronger lever than cutting all spending at once.",
                "priority": "low",
            })

    risk_profile = (model.get("risk_profile") or {}).get(risk_label, {"equity": 0.45, "bonds": 0.35, "cash": 0.2})
    if lang == "ru":
        risk_title = {"low": "Низкий риск", "medium": "Средний риск", "high": "Высокий риск"}.get(risk_label, risk_label_text)
        recommendations.append({
            "title": "Согласуйте портфель с уровнем риска",
            "detail": f"Для {risk_title.lower()} и {horizon_hint_ru} оптимальное распределение: {risk_profile.get('equity', 0.45):.0%} акции, {risk_profile.get('bonds', 0.35):.0%} облигации и {risk_profile.get('cash', 0.2):.0%} наличные средства.",
            "priority": "medium",
        })
    else:
        risk_title = {"low": "Low", "medium": "Medium", "high": "High"}.get(risk_label, risk_label_text)
        recommendations.append({
            "title": "Match your portfolio to your risk profile",
            "detail": f"For a {risk_title.lower()} risk profile and {horizon_hint}, a portfolio split of {risk_profile.get('equity', 0.45):.0%} equities, {risk_profile.get('bonds', 0.35):.0%} bonds and {risk_profile.get('cash', 0.2):.0%} cash fits your profile well.",
            "priority": "medium",
        })

    if current_savings <= 0:
        if lang == "ru":
            recommendations.append({
                "title": "Создайте резерв на черный день",
                "detail": "Отделяйте фиксированную сумму от каждого дохода, чтобы защитить стабильность до начала более агрессивного инвестирования.",
                "priority": "high",
            })
        else:
            recommendations.append({
                "title": "Build an emergency reserve",
                "detail": "Set aside a fixed amount every paycheck so your finances stay stable before you invest more aggressively.",
                "priority": "high",
            })

    if not recommendations:
        if lang == "ru":
            recommendations.append({
                "title": "Поддерживайте стабильный денежный поток",
                "detail": "Ваши привычки сбалансированы. Продолжайте отслеживать расходы и сохранять ежемесячный surplus для достижения целей.",
                "priority": "low",
            })
        else:
            recommendations.append({
                "title": "Keep a steady cash flow",
                "detail": "Your habits are balanced. Continue tracking spending and keep a monthly surplus to accelerate your goals.",
                "priority": "low",
            })

    # Keep recommendations focused and helpful; more than four hints is welcome for the Home section.
    unique = []
    seen = set()
    for item in recommendations:
        key = (item["title"], item["detail"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique[:6]

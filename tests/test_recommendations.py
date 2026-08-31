import unittest

from backend.finance.news import fetch_market_snapshot
from backend.finance.recommendations import (
    build_personalized_recommendations,
    train_recommendation_model,
)


class RecommendationModelTest(unittest.TestCase):
    def test_train_recommendation_model_creates_model(self):
        model = train_recommendation_model(
            [
                {"category": "Food", "amount": 12000, "kind": "expense"},
                {"category": "Food", "amount": 8000, "kind": "expense"},
                {"category": "Housing", "amount": 25000, "kind": "expense"},
                {"category": "Entertainment", "amount": 3000, "kind": "expense"},
                {"category": "Salary", "amount": 120000, "kind": "income"},
            ]
        )
        self.assertIn("category_spending", model)
        self.assertIn("savings_target", model)

    def test_build_personalized_recommendations_uses_profile_data(self):
        recommendations = build_personalized_recommendations(
            profile={"risk_level": "medium", "investment_horizon": "3-5 years", "current_savings": 150000},
            transactions=[
                {"kind": "income", "amount": 120000, "category": "Salary"},
                {"kind": "expense", "amount": 15000, "category": "Food"},
                {"kind": "expense", "amount": 20000, "category": "Housing"},
                {"kind": "expense", "amount": 6000, "category": "Transport"},
            ],
            model={
                "category_spending": {"Food": 0.15, "Housing": 0.25, "Transport": 0.08, "Entertainment": 0.1},
                "savings_target": 0.2,
                "risk_profile": {"low": {"equity": 0.2, "bonds": 0.5, "cash": 0.3}, "medium": {"equity": 0.5, "bonds": 0.3, "cash": 0.2}},
            },
        )
        self.assertTrue(len(recommendations) >= 2)
        self.assertTrue(all("title" in item for item in recommendations))

    def test_monthly_spending_recommendations_are_richer_and_category_based(self):
        recommendations = build_personalized_recommendations(
            profile={"risk_level": "high", "investment_horizon": "1 year", "current_savings": 0},
            transactions=[
                {"kind": "income", "amount": 100000, "category": "Salary"},
                {"kind": "expense", "amount": 65000, "category": "Food"},
                {"kind": "expense", "amount": 20000, "category": "Housing"},
                {"kind": "expense", "amount": 15000, "category": "Transport"},
                {"kind": "expense", "amount": 10000, "category": "Shopping"},
            ],
            model={
                "category_spending": {"Food": 0.22, "Housing": 0.18, "Transport": 0.12, "Shopping": 0.08},
                "savings_target": 0.25,
                "risk_profile": {"high": {"equity": 0.7, "bonds": 0.2, "cash": 0.1}},
            },
            lang="en",
        )
        self.assertGreaterEqual(len(recommendations), 4)
        titles = " ".join(item["title"] for item in recommendations)
        self.assertIn("Food", titles)
        self.assertTrue(any("savings" in item["title"].lower() or "savings" in item["detail"].lower() for item in recommendations))

    def test_fetch_market_snapshot_returns_rates(self):
        snapshot = fetch_market_snapshot(lang="ru")
        self.assertIn("key_rate", snapshot)
        self.assertIn("usd", snapshot)
        self.assertIn("eur", snapshot)
        self.assertTrue(isinstance(snapshot["key_rate"], (int, float)))
        self.assertTrue(isinstance(snapshot["usd"], (int, float)))
        self.assertTrue(isinstance(snapshot["eur"], (int, float)))


if __name__ == "__main__":
    unittest.main()

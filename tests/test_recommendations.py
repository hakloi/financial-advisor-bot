import unittest

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


if __name__ == "__main__":
    unittest.main()

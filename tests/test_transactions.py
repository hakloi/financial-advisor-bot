import unittest # Standard framework for writing and running automated unit tests
from datetime import date # Import date 
from unittest.mock import patch # Module used for replacing parts of your system under test with mock objects

from fastapi import HTTPException # Web framework, raise HTTP exceptions

from backend.api.routers.users import add_user_transaction, update_user_transaction, delete_user_transaction # Function under test
from backend.api.schemas.schemas import TransactionCreate # Pydantic schema for transaction data


# Class for testing the transaction API
class TransactionApiTest(unittest.TestCase):
    current_user = {"id": 7, "username": "tester"}

    # Test that the add_user_transaction function correctly adds an income transaction and returns the expected result
    @patch("backend.api.routers.users.create_transaction")
    def test_add_income(self, create_transaction):
        expected = {
            "id": 1,
            "entry_date": date(2026, 8, 28),
            "kind": "income",
            "amount": 1250.0,
            "currency": "RUB",
            "category": None,
            "description": "Salary",
        }
        create_transaction.return_value = expected

        result = add_user_transaction(
            TransactionCreate(
                entry_date=date(2026, 8, 28),
                kind="income",
                amount=1250,
                description="Salary",
            ),
            self.current_user,
        )

        self.assertEqual(result, expected)
        create_transaction.assert_called_once_with(7, date(2026, 8, 28), "income", 1250, "Salary", "RUB", None)

    # Test that the add_user_transaction function correctly adds an expense transaction and returns the expected result
    def test_rejects_invalid_transaction_type(self):
        with self.assertRaises(HTTPException) as context:
            add_user_transaction(
                TransactionCreate(entry_date=date(2026, 8, 28), kind="transfer", amount=10),
                self.current_user,
            )

        self.assertEqual(context.exception.status_code, 400)

    # Test that the add_user_transaction function raises an HTTPException when a negative amount is provided
    def test_rejects_negative_amount(self):
        with self.assertRaises(HTTPException) as context:
            add_user_transaction(
                TransactionCreate(entry_date=date(2026, 8, 28), kind="expense", amount=-10),
                self.current_user,
            )

        self.assertEqual(context.exception.status_code, 400)

    @patch("backend.api.routers.users.update_transaction")
    def test_update_transaction(self, update_transaction):
        expected = {
            "id": 12,
            "entry_date": date(2026, 8, 28),
            "kind": "income",
            "amount": 5000.0,
            "currency": "RUB",
            "category": "Salary",
            "description": "Bonus",
        }
        update_transaction.return_value = expected

        result = update_user_transaction(
            12,
            TransactionCreate(
                entry_date=date(2026, 8, 28),
                kind="income",
                amount=5000,
                currency="RUB",
                category="Salary",
                description="Bonus",
            ),
            self.current_user,
        )

        self.assertEqual(result, expected)
        update_transaction.assert_called_once_with(7, 12, date(2026, 8, 28), "income", 5000, "Bonus", "RUB", "Salary")

    @patch("backend.api.routers.users.delete_transaction")
    def test_delete_transaction(self, delete_transaction):
        delete_transaction.return_value = True

        result = delete_user_transaction(12, self.current_user)

        self.assertTrue(result)
        delete_transaction.assert_called_once_with(7, 12)


if __name__ == "__main__":
    unittest.main()

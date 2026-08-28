import unittest
from datetime import date
from unittest.mock import patch

from fastapi import HTTPException

from backend.api.routers.users import add_user_transaction
from backend.api.schemas.schemas import TransactionCreate


class TransactionApiTest(unittest.TestCase):
    current_user = {"id": 7, "username": "tester"}

    @patch("backend.api.routers.users.create_transaction")
    def test_add_income(self, create_transaction):
        expected = {
            "id": 1,
            "entry_date": date(2026, 8, 28),
            "kind": "income",
            "amount": 1250.0,
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
        create_transaction.assert_called_once_with(7, date(2026, 8, 28), "income", 1250, "Salary")

    def test_rejects_invalid_transaction_type(self):
        with self.assertRaises(HTTPException) as context:
            add_user_transaction(
                TransactionCreate(entry_date=date(2026, 8, 28), kind="transfer", amount=10),
                self.current_user,
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_rejects_negative_amount(self):
        with self.assertRaises(HTTPException) as context:
            add_user_transaction(
                TransactionCreate(entry_date=date(2026, 8, 28), kind="expense", amount=-10),
                self.current_user,
            )

        self.assertEqual(context.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()

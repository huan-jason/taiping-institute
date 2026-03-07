from datetime import date
from typing import Any
from django.utils import timezone
from taiping.models import Instructor


class RevenueMixin:

    def revenue__get_bar_heights(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        min_amount, max_amount = self.revenue__get_chart_min_max_amounts(data)
        total: float = (max_amount - min_amount) or max_amount
        low: float = 0 if min_amount == max_amount else (min_amount - total * 0.1)
        unit_val: float = (100 / total) if total else 0

        for item in data:
            amount: float = item["amount"]
            val: float = max(amount - low, 0)
            item["height"] = f"{int(val * unit_val)}"

        return data

    def revenue__get_chart_min_max_amounts(self, data: list[dict[str, Any]]) -> tuple[float, float]:
        amounts: list[float] = [amount for item in data if (amount := item["amount"])] or [0]
        min_amount: float = min(amounts)
        max_amount: float = max(amounts)
        return min_amount, max_amount

    def revenue__get_previous_month(self, month: date) -> date:
        month_: int = month.month - 1
        year_: int = month.year

        return month.replace(
            month=month_ or 12,
            year=year_ if month_ else year_ - 1,
        )

    def revenue__get_revenues(self, instructor: Instructor, months: int = 6) -> list[dict[str, Any]]:
        month: date = timezone.now().date().replace(day=1)
        revenues: list[dict[str, Any]] = []

        for item in range(months):
            revenues.append({
                "month": month,
                "amount": instructor.get_revenue(month),
                "height": 0,
            })
            month = self.revenue__get_previous_month(month)

        return self.revenue__get_bar_heights(revenues[::-1])

    def revenue__get_ytd_amount(self, instructor: Instructor) -> float:
        month: date = timezone.now().date().replace(day=1)
        year: int = month.year
        amount: float = 0

        while month.year == year:
            amount += instructor.get_revenue(month)
            month = self.revenue__get_previous_month(month)

        return amount

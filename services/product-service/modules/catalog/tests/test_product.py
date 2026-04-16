from django.test import TestCase
from decimal import Decimal
from modules.catalog.domain.entities.product import Product
from modules.catalog.domain.value_objects.money import Money


class ProductEntityTest(TestCase):
    def _make_product(self, stock=5):
        return Product(
            id=1, title="Test Book", author="Test Author",
            description="", price=Decimal("100"), stock=stock,
            category_id=1, collection_ids=[], attributes={}, cover_image=None
        )

    def test_is_in_stock(self):
        self.assertTrue(self._make_product(stock=5).is_in_stock())

    def test_not_in_stock(self):
        self.assertFalse(self._make_product(stock=0).is_in_stock())

    def test_update_stock(self):
        product = self._make_product()
        product.update_stock(10)
        self.assertEqual(product.stock, 10)

    def test_update_stock_negative_raises(self):
        product = self._make_product()
        with self.assertRaises(ValueError):
            product.update_stock(-1)


class MoneyValueObjectTest(TestCase):
    def test_valid_money(self):
        m = Money(amount=Decimal("50000"))
        self.assertEqual(m.amount, Decimal("50000"))
        self.assertEqual(m.currency, "VND")

    def test_negative_money_raises(self):
        with self.assertRaises(ValueError):
            Money(amount=Decimal("-1"))

    def test_money_is_immutable(self):
        m = Money(amount=Decimal("100"))
        with self.assertRaises(Exception):
            m.amount = Decimal("200")

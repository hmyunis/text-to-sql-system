import random

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import Customer, Order, Product


class Command(BaseCommand):
    help = "Clear all data and populate the database with mock data."

    def handle(self, *args, **options):
        rng = random.Random()
        names = [
            "Abebe", "Alemu", "Bekele", "Dawit", "Elias", "Fikre", "Girma",
            "Hailu", "Kebede", "Lemma", "Mulu", "Solomon", "Tadesse", "Tsegaye",
            "Yonas", "Mesfin", "Getachew", "Tesfaye", "Worku", "Zeleke",
            "Selam", "Emebet", "Haregewoin", "Genet", "Rahel", "Meron",
            "Saba", "Eden", "Ahmed", "Ali", "Mohammed", "Mustafa", "Omar",
            "Hassan", "Hussein", "Hamza", "Ibrahim", "Abdullahi", "Fatima",
            "Aisha", "Maryam", "Khadija", "Zainab", "Safiya",
        ]
        cities = [
            "Addis Ababa", "Dire Dawa", "Mekelle", "Bahir Dar", "Hawassa",
            "Adama", "Jimma", "Harar", "Gondar", "Dessie", "Jijiga", "Axum",
        ]
        product_data = [
            {"name": "Yirgacheffe Coffee Beans", "price": "18.50", "category": "Coffee"},
            {"name": "Sidamo Coffee Beans", "price": "17.00", "category": "Coffee"},
            {"name": "Ethiopian Tea Leaves", "price": "6.75", "category": "Tea"},
            {"name": "Berbere Spice Blend", "price": "4.25", "category": "Spices"},
            {"name": "Mitmita Chili Mix", "price": "3.90", "category": "Spices"},
            {"name": "Teff Flour 1kg", "price": "7.20", "category": "Grains"},
            {"name": "Injera Starter Kit", "price": "9.80", "category": "Grains"},
            {"name": "Traditional Basket (Mesob)", "price": "25.00", "category": "Crafts"},
            {"name": "Handwoven Shawl", "price": "22.50", "category": "Textiles"},
            {"name": "Cotton Scarf", "price": "12.00", "category": "Textiles"},
            {"name": "Leather Wallet", "price": "15.75", "category": "Leather"},
            {"name": "Sheba Honey Jar", "price": "8.50", "category": "Food"},
            {"name": "Spiced Honey Wine (Tej)", "price": "19.00", "category": "Beverages"},
            {"name": "Incense Pack", "price": "5.50", "category": "Home"},
            {"name": "Clay Coffee Pot (Jebena)", "price": "14.25", "category": "Home"},
            {"name": "Beaded Necklace", "price": "11.90", "category": "Jewelry"},
            {"name": "Silver Ring", "price": "28.00", "category": "Jewelry"},
            {"name": "Ethiopian History Book", "price": "13.40", "category": "Books"},
            {"name": "Amharic Phrasebook", "price": "9.60", "category": "Books"},
            {"name": "Handcrafted Drum", "price": "32.00", "category": "Music"},
            {"name": "Notebook Set", "price": "6.20", "category": "Stationery"},
            {"name": "Natural Soap Bar", "price": "4.80", "category": "Personal Care"},
            {"name": "Aloe Skin Balm", "price": "7.95", "category": "Personal Care"},
        ]

        with transaction.atomic():
            Order.objects.all().delete()
            Product.objects.all().delete()
            Customer.objects.all().delete()

            customers = []
            for index in range(20):
                name = rng.choice(names)
                customers.append(
                    Customer(
                        name=name,
                        email=f"{name.lower()}.{index}@example.com",
                        city=rng.choice(cities),
                    )
                )
            Customer.objects.bulk_create(customers)
            customers = list(Customer.objects.all())

            products = [Product(**data) for data in product_data[:20]]
            Product.objects.bulk_create(products)
            products = list(Product.objects.all())

            orders = []
            for _ in range(20):
                orders.append(
                    Order(
                        customer=rng.choice(customers),
                        product=rng.choice(products),
                        quantity=rng.randint(1, 8),
                    )
                )
            Order.objects.bulk_create(orders)

        self.stdout.write(self.style.SUCCESS("Mock data created."))

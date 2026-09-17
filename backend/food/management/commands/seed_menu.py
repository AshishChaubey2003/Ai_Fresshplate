"""Fill the menu with sample dishes: python manage.py seed_menu

Safe to run more than once - it updates existing dishes instead of duplicating them.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from food.models import Category, FoodItem

# (category, name, description, price, discount, veg, prep_min, calories, status)
DISHES = [
    ("Starters", "Paneer Tikka", "Cottage cheese marinated in yoghurt and spices, grilled in the tandoor.", "260", "220", True, 20, 280, "available"),
    ("Starters", "Chilli Garlic Mushroom", "Button mushrooms tossed with garlic, chilli and spring onion.", "230", None, True, 18, 210, "available"),
    ("Starters", "Chicken Seekh Kebab", "Minced chicken with green chilli and coriander, char-grilled on skewers.", "310", None, False, 25, 340, "available"),
    ("Starters", "Honey Chilli Potato", "Crisp potato batons in a sweet and spicy glaze with sesame.", "190", "160", True, 15, 380, "available"),

    ("Main Course", "Dal Makhani", "Black lentils simmered overnight with butter, cream and tomato.", "240", "200", True, 25, 320, "available"),
    ("Main Course", "Paneer Butter Masala", "Paneer in a rich tomato and cashew gravy, finished with cream.", "290", None, True, 25, 450, "available"),
    ("Main Course", "Chicken Biryani", "Long-grain basmati layered with marinated chicken and whole spices.", "320", "280", False, 35, 550, "available"),
    ("Main Course", "Mutton Rogan Josh", "Slow-cooked mutton in a Kashmiri chilli and yoghurt gravy.", "420", None, False, 45, 620, "available"),
    ("Main Course", "Veg Thali", "Two sabzis, dal, rice, four rotis, salad and a sweet.", "260", None, True, 20, 700, "available"),
    ("Main Course", "Chole Bhature", "Spiced chickpeas with two puffed bhature and pickled onion.", "210", None, True, 20, 680, "available"),

    ("Breads & Rice", "Butter Naan", "Tandoori naan brushed with white butter.", "60", None, True, 10, 180, "available"),
    ("Breads & Rice", "Laccha Paratha", "Layered whole wheat paratha, crisp outside and soft inside.", "70", None, True, 12, 220, "available"),
    ("Breads & Rice", "Jeera Rice", "Basmati rice tempered with cumin and ghee.", "150", None, True, 15, 290, "available"),

    ("Desserts", "Gulab Jamun", "Two warm milk dumplings soaked in cardamom syrup.", "110", None, True, 5, 300, "available"),
    ("Desserts", "Gajar Ka Halwa", "Slow-cooked carrot halwa with khoya and almonds.", "140", None, True, 8, 350, "available"),

    ("Beverages", "Masala Chai", "Assam tea brewed with ginger, cardamom and milk.", "50", None, True, 8, 90, "available"),
    ("Beverages", "Sweet Lassi", "Thick curd blended with sugar, topped with malai.", "90", None, True, 6, 220, "available"),
    ("Beverages", "Fresh Lime Soda", "Lime, soda and a pinch of black salt.", "70", None, True, 5, 60, "available"),

    # Rescue deals - surplus food sold cheap instead of being thrown away
    ("Main Course", "Veg Pulao (rescue deal)", "Today's surplus pulao from the lunch batch, still fresh.", "180", "90", True, 10, 400, "rescue"),
    ("Starters", "Assorted Snack Box (rescue deal)", "Mixed evening snacks left from a cancelled bulk order.", "200", "99", True, 10, 450, "rescue"),
]

CATEGORY_NOTES = {
    "Starters": "Small plates to begin the meal",
    "Main Course": "Full meals, cooked to order",
    "Breads & Rice": "Fresh from the tandoor and the rice pot",
    "Desserts": "Something sweet to finish",
    "Beverages": "Hot and cold drinks",
}


class Command(BaseCommand):
    help = "Create sample categories and dishes for the menu."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-images",
            action="store_true",
            help="Also fetch a random food photo for each dish from the Foodish API.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete dishes that have never been ordered before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            removed = 0
            for item in FoodItem.objects.all():
                # Dishes that appear in an order must stay, or order history breaks
                if not item.orderitem_set.exists():
                    item.delete()
                    removed += 1
            self.stdout.write(f"Removed {removed} unused dishes.")

        categories = {}
        for name, note in CATEGORY_NOTES.items():
            category, _ = Category.objects.get_or_create(
                name=name, defaults={"description": note}
            )
            categories[name] = category

        created = updated = 0
        for row in DISHES:
            cat, name, desc, price, discount, is_veg, prep, cals, status = row
            item, was_created = FoodItem.objects.update_or_create(
                name=name,
                defaults={
                    "category": categories[cat],
                    "description": desc,
                    "price": Decimal(price),
                    "discount_price": Decimal(discount) if discount else None,
                    "is_veg": is_veg,
                    "preparation_time": prep,
                    "calories": cals,
                    "status": status,
                    "is_available": True,
                },
            )
            created += was_created
            updated += not was_created

            if options["with_images"] and not item.image_url:
                url = self._fetch_image()
                if url:
                    item.image_url = url
                    item.save(update_fields=["image_url"])

        self.stdout.write(self.style.SUCCESS(
            f"Menu ready: {created} dishes created, {updated} updated, "
            f"{len(categories)} categories."
        ))

    def _fetch_image(self):
        """Foodish serves free random food photos. A failure here is harmless -
        the frontend falls back to an emoji when a dish has no image."""
        try:
            import requests

            response = requests.get("https://foodish-api.com/api/", timeout=6)
            response.raise_for_status()
            return response.json().get("image", "")
        except Exception as exc:
            self.stderr.write(f"Image fetch failed ({exc}); leaving it blank.")
            return ""
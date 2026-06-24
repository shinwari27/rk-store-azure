"""
RK Store — Seed Products Command (Stage 3)

Inserts all 12 iPhone products into the Azure SQL Database.

Usage:
    python manage.py seed_products           # insert all 12 products
    python manage.py seed_products --clear   # delete existing and re-insert
"""

from django.core.management.base import BaseCommand
from store.models import Product


PRODUCTS = [
    {
        'name':             'iPhone 17 Pro Max',
        'storage':          '512GB',
        'color':            'Black Titanium',
        'condition':        'New',
        'price':            1399.00,
        'original_price':   None,
        'stock':            15,
        'warranty':         '1-Year Apple',
        'battery_health':   None,
        'description':      'The most powerful iPhone ever. A19 Pro chip with ProMotion display, titanium frame, 5x optical zoom, and ProRes 4K video. Apple Intelligence transforms everything you do.',
        'is_featured':      True,
        'is_latest':        True,
        'is_special_offer': False,
        'is_limited':       False,
    },
    {
        'name':             'iPhone 17 Pro',
        'storage':          '256GB',
        'color':            'Natural Titanium',
        'condition':        'New',
        'price':            1199.00,
        'original_price':   None,
        'stock':            20,
        'warranty':         '1-Year Apple',
        'battery_health':   None,
        'description':      'The thinnest Pro iPhone ever. A19 Pro chip with Camera Control, Apple Intelligence, and an advanced triple-camera system. Redefining what is possible.',
        'is_featured':      True,
        'is_latest':        True,
        'is_special_offer': False,
        'is_limited':       False,
    },
    {
        'name':             'iPhone 17',
        'storage':          '128GB',
        'color':            'Midnight',
        'condition':        'New',
        'price':            999.00,
        'original_price':   None,
        'stock':            30,
        'warranty':         '1-Year Apple',
        'battery_health':   None,
        'description':      'The future of iPhone. Thinner and lighter than ever with A19 chip, Apple Intelligence built in, and a redesigned camera system that changes how you see the world.',
        'is_featured':      True,
        'is_latest':        True,
        'is_special_offer': False,
        'is_limited':       False,
    },
    {
        'name':             'iPhone 17 Plus',
        'storage':          '256GB',
        'color':            'Teal',
        'condition':        'New',
        'price':            1099.00,
        'original_price':   None,
        'stock':            3,
        'warranty':         '1-Year Apple',
        'battery_health':   None,
        'description':      'Big screen, all-day battery, and Apple Intelligence. Only 3 units remaining. The iPhone 17 Plus with A19 chip in a stunning Teal finish.',
        'is_featured':      False,
        'is_latest':        True,
        'is_special_offer': False,
        'is_limited':       True,
    },
    {
        'name':             'iPhone 16 Pro Max',
        'storage':          '256GB',
        'color':            'Desert Titanium',
        'condition':        'New',
        'price':            1099.00,
        'original_price':   1299.00,
        'stock':            8,
        'warranty':         '1-Year Apple',
        'battery_health':   None,
        'description':      'A18 Pro chip, Camera Control, titanium design, and Apple Intelligence. Our biggest deal of the year — save $200 while supplies last.',
        'is_featured':      True,
        'is_latest':        False,
        'is_special_offer': True,
        'is_limited':       False,
    },
    {
        'name':             'iPhone 16 Pro',
        'storage':          '128GB',
        'color':            'White Titanium',
        'condition':        'New',
        'price':            1099.00,
        'original_price':   None,
        'stock':            12,
        'warranty':         '1-Year Apple',
        'battery_health':   None,
        'description':      'A18 Pro chip, 5x optical zoom, Camera Control, and Apple Intelligence. The pro camera experience perfected in brilliant White Titanium.',
        'is_featured':      False,
        'is_latest':        False,
        'is_special_offer': False,
        'is_limited':       False,
    },
    {
        'name':             'iPhone 16',
        'storage':          '128GB',
        'color':            'Ultramarine',
        'condition':        'New',
        'price':            799.00,
        'original_price':   899.00,
        'stock':            25,
        'warranty':         '1-Year Apple',
        'battery_health':   None,
        'description':      'A18 chip with Apple Intelligence and Camera Control. 48MP Fusion camera with spatial audio. Save $100 today in stunning Ultramarine.',
        'is_featured':      False,
        'is_latest':        False,
        'is_special_offer': True,
        'is_limited':       False,
    },
    {
        'name':             'iPhone 16 Plus',
        'storage':          '128GB',
        'color':            'Rose',
        'condition':        'New',
        'price':            799.00,
        'original_price':   None,
        'stock':            2,
        'warranty':         '1-Year Apple',
        'battery_health':   None,
        'description':      'Bigger display and all-day battery. A18 chip with Apple Intelligence in beautiful Rose. Only 2 units remaining.',
        'is_featured':      False,
        'is_latest':        False,
        'is_special_offer': False,
        'is_limited':       True,
    },
    {
        'name':             'iPhone 16 Pro Max',
        'storage':          '512GB',
        'color':            'Black Titanium',
        'condition':        'Used',
        'price':            999.00,
        'original_price':   None,
        'stock':            5,
        'warranty':         '90-Day Certified',
        'battery_health':   '95%',
        'description':      'Certified pre-owned. Fully inspected, factory reset, and tested. Near-new condition with A18 Pro chip and premium titanium design.',
        'is_featured':      False,
        'is_latest':        False,
        'is_special_offer': False,
        'is_limited':       False,
    },
    {
        'name':             'iPhone 15 Pro Max',
        'storage':          '256GB',
        'color':            'White Titanium',
        'condition':        'Used',
        'price':            799.00,
        'original_price':   None,
        'stock':            7,
        'warranty':         '90-Day Certified',
        'battery_health':   '90%',
        'description':      'Certified pre-owned iPhone 15 Pro Max in White Titanium. A17 Pro chip, titanium frame. Fully inspected and tested. Excellent condition.',
        'is_featured':      False,
        'is_latest':        False,
        'is_special_offer': False,
        'is_limited':       False,
    },
    {
        'name':             'iPhone 15 Pro',
        'storage':          '256GB',
        'color':            'Blue Titanium',
        'condition':        'Used',
        'price':            699.00,
        'original_price':   None,
        'stock':            6,
        'warranty':         '90-Day Certified',
        'battery_health':   '92%',
        'description':      'Certified pre-owned in Blue Titanium. A17 Pro chip, USB-C, and titanium design. Excellent condition at exceptional value.',
        'is_featured':      False,
        'is_latest':        False,
        'is_special_offer': False,
        'is_limited':       False,
    },
    {
        'name':             'iPhone 15',
        'storage':          '128GB',
        'color':            'Pink',
        'condition':        'Used',
        'price':            549.00,
        'original_price':   None,
        'stock':            10,
        'warranty':         '90-Day Certified',
        'battery_health':   '88%',
        'description':      'Certified pre-owned iPhone 15 in Pink. Dynamic Island, 48MP camera, USB-C. The perfect entry-level iPhone at an unbeatable price.',
        'is_featured':      False,
        'is_latest':        False,
        'is_special_offer': False,
        'is_limited':       False,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with all 12 RK Store iPhone products.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing products before seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Product.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'🗑️  Deleted {count} existing products.'))

        created = 0
        skipped = 0

        for data in PRODUCTS:
            product, was_created = Product.objects.get_or_create(
                name=data['name'],
                storage=data['storage'],
                color=data['color'],
                condition=data['condition'],
                defaults=data,
            )
            if was_created:
                created += 1
                self.stdout.write(f"  ✅ Created: {product}")
            else:
                skipped += 1
                self.stdout.write(f"  ⏭️  Skipped (already exists): {product}")

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'🎉 Seeding complete — {created} created, {skipped} skipped.'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'📦 Total products in database: {Product.objects.count()}'
        ))

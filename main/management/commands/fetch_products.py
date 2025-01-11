import requests
from django.core.management.base import BaseCommand
from main.models import Product
import random

API_URL = "https://www.googleapis.com/books/v1/volumes"

class Command(BaseCommand):
    help = "Fetch products from API and save to database"

    def handle(self, *args, **kwargs):
        response = requests.get(f"{API_URL}?q=education+OR+learning+OR+study+materials")
        data = response.json()

        for item in data.get('items', []):
            title = item['volumeInfo']['title']
            thumbnail = item['volumeInfo'].get('imageLinks', {}).get('thumbnail', 'https://via.placeholder.com/150')
            raw_price = random.randint(50000, 500000)
            formatted_price = f"{raw_price:,} VND"
            preview_link = item['volumeInfo'].get('previewLink', '#')

            Product.objects.update_or_create(
                title=title,
                defaults={
                    'thumbnail': thumbnail,
                    'raw_price': raw_price,
                    'formatted_price': formatted_price,
                    'preview_link': preview_link,
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully fetched and saved products'))

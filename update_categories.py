import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classifieds.settings')
django.setup()

from ads.models import MainCategory, SubCategory, SubSubCategory
from django.utils.text import slugify

# Список категорий и подкатегорий
CATEGORIES = {
    'Sell-Rent': {
        'Real Estate': [],
        'Vehicles': ['Cars', 'Trucks', 'Motorcycles', 'Commercial', 'Other'],
        'Computers': ['Desktop PC', 'Laptops', 'Monitors', 'Printer & Scanners', 'Accessories & Parts'],
        'Phones and Tablets': ['Phones', 'Tablets', 'Smart Watches', 'Accessories & Parts'],
        'Electronics': ['Smartphones & Tablets', 'TVs & Home Theater', 'Cameras & Photography', 'Audio Equipment', 'Video Games & Consoles'],
        'Home & Garden': ['Furniture', 'Appliances', 'Home Decor', 'Tools & Hardware', 'Outdoor & Garden Equipment', 'Indoor & Lighting'],
        'Clothing & Accessories': ['Men\'s Clothing', 'Women\'s Clothing', 'Shoes', 'Jewelry & Watches', 'Handbags & Accessories'],
        'Baby & Kids': ['Baby Clothing', 'Toys & Games', 'Baby Gear & Equipment', 'Kids\' Furniture'],
        'Food & Grocery': ['Packaged Foods', 'Specialty & Ethnic Foods', 'Beverages', 'Homemade & Artisan Foods'],
        'Pets & Animals': ['Dogs', 'Cats', 'Birds', 'Fish & Aquatic Pets', 'Small Animals (rabbits, hamsters, etc.)', 'Pet Supplies & Accessories'],
        'Equipment & Tools': ['Construction Equipment', 'Party & Event Equipment', 'Sporting Goods', 'Business Equipment'],
        'Art': ['Books & Magazines', 'Tickets & Vouchers', 'Musical Instruments', 'Miscellaneous Items', 'Collectibles & Art']
    }
}

def update_categories():
    for main_cat_name, subcats in CATEGORIES.items():
        # Получаем существующую категорию
        main_cat = MainCategory.objects.get(name=main_cat_name)
        print(f"Main Category: {main_cat_name} found")

        # Удаляем старые подкатегории, кроме Real Estate
        SubCategory.objects.filter(main_category=main_cat).exclude(name='Real Estate').delete()

        # Добавляем новые подкатегории
        for subcat_name, subsubcats in subcats.items():
            if subcat_name == 'Real Estate':
                # Обновляем существующую подкатегорию Real Estate
                subcat = SubCategory.objects.get(main_category=main_cat, name=subcat_name)
                print(f"  Sub Category: {subcat_name} found")
            else:
                # Создаем новые подкатегории
                subcat = SubCategory.objects.create(
                    main_category=main_cat,
                    name=subcat_name,
                    slug=slugify(subcat_name),
                    icon='fa-folder'  # Иконка по умолчанию
                )
                print(f"  Sub Category: {subcat_name} created")

            # Добавляем подподкатегории
            for subsubcat_name in subsubcats:
                # Создаем уникальный slug, добавляя название подкатегории
                unique_slug = f"{slugify(subcat_name)}-{slugify(subsubcat_name)}"
                subsubcat = SubSubCategory.objects.create(
                    main_category=main_cat,
                    sub_category=subcat,
                    name=subsubcat_name,
                    slug=unique_slug,
                    icon='fa-file',  # Иконка по умолчанию
                    cost=0.0
                )
                print(f"    Sub Sub Category: {subsubcat_name} created")

if __name__ == '__main__':
    update_categories() 
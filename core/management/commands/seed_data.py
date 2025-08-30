from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from core.models import Category, MenuItem
import re
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed menu/items from ref.html and create roles/users'

    def parse_menu(self, text):
        start = text.find('const menuData = {')
        if start == -1:
            return None
        end = text.find('};', start)
        if end == -1:
            return None
        block = text[start:end+1]
        def parse_section(name):
            m = re.search(rf"{name}\s*:\s*\[(.*?)\]", block, re.S)
            items = []
            if not m:
                return items
            arr = m.group(1)
            for id_, n, p, d in re.findall(r"\{\s*id:\s*(\d+),\s*name:\s*\"([^\"]+)\",\s*price:\s*([0-9.]+),\s*description:\s*\"([^\"]*)\"\s*\}", arr):
                items.append({
                    'id': int(id_),
                    'name': n,
                    'price': Decimal(p),
                    'description': d,
                })
            return items
        return {
            'paan': parse_section('paan'),
            'tobacco': parse_section('tobacco'),
        }

    def handle(self, *args, **options):
        base = settings.BASE_DIR
        ref_path = base / 'ref.html'
        text = ref_path.read_text(encoding='utf-8')
        data = self.parse_menu(text)
        if not data:
            self.stdout.write(self.style.ERROR('menuData not found'))
            return

        paan_cat, _ = Category.objects.get_or_create(name='Paan')
        tobacco_cat, _ = Category.objects.get_or_create(name='Tobacco')
        count = 0
        for item in data.get('paan', []):
            _, created = MenuItem.objects.get_or_create(
                name=item['name'],
                defaults={
                    'category': paan_cat,
                    'price': item['price'],
                    'description': item.get('description', ''),
                    'active': True,
                }
            )
            count += int(created)
        for item in data.get('tobacco', []):
            _, created = MenuItem.objects.get_or_create(
                name=item['name'],
                defaults={
                    'category': tobacco_cat,
                    'price': item['price'],
                    'description': item.get('description', ''),
                    'active': True,
                }
            )
            count += int(created)

        # Create groups and permissions
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        from core.models import Bill
        bill_ct = ContentType.objects.get_for_model(Bill)
        can_export_perm, _ = Permission.objects.get_or_create(codename='can_export_bills', name='Can export bills', content_type=bill_ct)
        # Ensure Manager does NOT have export perm
        if manager_group.permissions.filter(id=can_export_perm.id).exists():
            manager_group.permissions.remove(can_export_perm)

        # Create users
        if not User.objects.filter(username='vijay').exists():
            User.objects.create_superuser('vijay', password='Vijay@099791')
            self.stdout.write(self.style.SUCCESS('Created admin user vijay'))
        else:
            self.stdout.write('Admin user vijay already exists')

        if not User.objects.filter(username='sadam').exists():
            sadam = User.objects.create_user('sadam', password='sadam@01')
            sadam.groups.add(manager_group)
            self.stdout.write(self.style.SUCCESS('Created manager user sadam'))
        else:
            self.stdout.write('Manager user sadam already exists')

        self.stdout.write(self.style.SUCCESS(f'Seeding completed. New items created: {count}'))

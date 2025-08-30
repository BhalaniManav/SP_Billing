from rest_framework import serializers
from core.models import Category, MenuItem, Bill, BillItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'description', 'category', 'category_id', 'active']


class BillItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source='item', write_only=True
    )

    class Meta:
        model = BillItem
        fields = ['id', 'item', 'item_id', 'quantity', 'unit_price', 'line_total']
        read_only_fields = ['unit_price', 'line_total']


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True)

    class Meta:
        model = Bill
        fields = ['id', 'bill_no', 'customer_name', 'customer_contact', 'created_at', 'created_by', 'payment_method', 'total', 'items']
        read_only_fields = ['created_at', 'created_by', 'total']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        bill = Bill.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            menu_item = item_data['item']
            qty = item_data.get('quantity', 1)
            unit_price = menu_item.price
            line_total = unit_price * qty
            BillItem.objects.create(
                bill=bill,
                item=menu_item,
                quantity=qty,
                unit_price=unit_price,
                line_total=line_total,
            )
            total += line_total
        bill.total = total
        bill.save(update_fields=['total'])
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if items_data is not None:
            instance.items.all().delete()
            total = 0
            for item_data in items_data:
                menu_item = item_data['item']
                qty = item_data.get('quantity', 1)
                unit_price = menu_item.price
                line_total = unit_price * qty
                BillItem.objects.create(
                    bill=instance,
                    item=menu_item,
                    quantity=qty,
                    unit_price=unit_price,
                    line_total=line_total,
                )
                total += line_total
            instance.total = total
        instance.save()
        return instance

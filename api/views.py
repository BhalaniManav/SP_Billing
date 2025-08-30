from rest_framework import viewsets, permissions, decorators
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
import csv

from core.models import Category, MenuItem, Bill, BillItem
from .serializers import CategorySerializer, MenuItemSerializer, BillSerializer


class IsManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Manager').exists()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.filter(active=True).select_related('category').order_by('name')
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all().select_related('created_by').prefetch_related('items__item').order_by('-created_at')
    serializer_class = BillSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManagerOrAdmin()]
        return [permissions.IsAuthenticated()]


from .permissions import CanExportBills


@decorators.api_view(['GET'])
@decorators.permission_classes([CanExportBills])
def export_csv(request):
    # Only allow users with custom permission can_export_bills or superuser

    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    qs = Bill.objects.all()
    if from_date:
        qs = qs.filter(created_at__date__gte=from_date)
    if to_date:
        qs = qs.filter(created_at__date__lte=to_date)

    response = HttpResponse(content_type='text/csv')
    filename = f"sales_{timezone.now().date()}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['No','Date','Time','Bill By','Bill No','Customer','Contact','Total','Payment','Product','Qty','Price','Product Total'])

    counter = 1
    for bill in qs:
        items = bill.items.select_related('item')
        for bi in items:
            writer.writerow([
                counter,
                bill.created_at.date(),
                bill.created_at.time().strftime('%H:%M:%S'),
                bill.created_by.username if bill.created_by else '',
                bill.bill_no,
                bill.customer_name,
                bill.customer_contact,
                bill.total,
                bill.payment_method,
                bi.item.name,
                bi.quantity,
                bi.unit_price,
                bi.line_total,
            ])
        counter += 1
    return response

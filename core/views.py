from django.shortcuts import render, get_object_or_404, redirect
from .models import Sale, Item, SaleItem
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
import calendar
import qrcode, os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

# ---------- Access Control Checks ----------
def staff_check(user):
    return user.is_staff  # Staff-only pages

# ---------- Dashboard (Accessible to staff & admin) ----------
@login_required
def dashboard(request):
    total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_items = Item.objects.count()
    bank_transfers = Sale.objects.filter(payment_type='bank_transfer').count()
    recent_sales = Sale.objects.order_by('-date')[:5]

    sales_per_month = (
        Sale.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    chart_labels = [calendar.month_name[sale['month'].month] for sale in sales_per_month]
    chart_data = [float(sale['total']) for sale in sales_per_month]

    return render(request, 'core/dashboard.html', {
        'total_sales': total_sales,
        'total_items': total_items,
        'bank_transfers': bank_transfers,
        'recent_sales': recent_sales,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    })


# ---------- POS (Staff-only) ----------
@login_required
@user_passes_test(staff_check)
def pos(request):
    items = Item.objects.all()
    message = None

    if request.method == 'POST':
        discount = float(request.POST.get('discount', 0))
        payment_type = request.POST['payment_type']

        sale = Sale.objects.create(
            user=request.user,
            total_amount=0,
            discount=discount,
            payment_type=payment_type,
            date=timezone.now()
        )

        total_amount = 0
        items_data = [key for key in request.POST if key.startswith('items')]
        grouped = {}

        for key in items_data:
            idx = key.split('[')[1].split(']')[0]
            grouped.setdefault(idx, {})[key.split(']')[1][1:-1]] = request.POST[key]

        for idx, data in grouped.items():
            item = get_object_or_404(Item, id=data['id'])
            qty = int(data['qty'])

            if qty > item.stock_quantity:
                message = f"Not enough stock for {item.name}"
                sale.delete()
                break

            SaleItem.objects.create(sale=sale, item=item, quantity=qty, price=item.price)
            item.stock_quantity -= qty
            item.save()

            total_amount += item.price * qty

        sale.total_amount = total_amount - discount
        sale.save()

        if not message:
            message = f"Sale completed. Total ₦{sale.total_amount}"

    return render(request, 'core/pos.html', {'items': items, 'message': message})


# ---------- Items (Staff-only) ----------
@login_required
@user_passes_test(staff_check)
def items(request):
    all_items = Item.objects.all()
    return render(request, 'core/items.html', {'items': all_items})


# ---------- Receipt ----------
@login_required
@user_passes_test(staff_check)
def receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)

    subtotal = sum([i.quantity * i.price for i in sale.saleitem_set.all()])
    total = subtotal - sale.discount

    qr_data = f"Sale ID: {sale.id}, Total: ₦{total}"
    qr_img = qrcode.make(qr_data)
    qr_dir = os.path.join(settings.MEDIA_ROOT, "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)
    qr_path = os.path.join(qr_dir, f"receipt_{sale.id}.png")
    qr_img.save(qr_path)
    qr_code_url = settings.MEDIA_URL + "qr_codes/" + f"receipt_{sale.id}.png"

    html = render_to_string("core/receipt.html", {
        "sale": sale,
        "subtotal": subtotal,
        "total": total,
        "qr_code_url": qr_code_url
    })

    if request.GET.get("pdf") == "1":
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="receipt_{sale.id}.pdf"'
        pisa.CreatePDF(html, dest=response)
        return response

    return HttpResponse(html)


@login_required
@user_passes_test(staff_check)
def reports(request):
    return render(request, 'core/reports.html')

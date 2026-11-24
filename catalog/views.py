import json
import re
from urllib.parse import quote

from django.conf import settings
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Category, Inquiry, InquiryItem, Product


def home(request):
    return render(request, "home.html", {"featured_categories": Category.objects.filter(featured_on_home=True)})


def collection(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return render(
        request,
        "collection.html",
        {
            "category": category,
            "products": category.products.filter(is_active=True),
            "categories": Category.objects.all(),
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(
        request,
        "product_detail.html",
        {"product": product, "related": related, "max_qty": max(product.available_units, 1)},
    )


def gallery(request):
    return render(
        request,
        "gallery.html",
        {
            "categories": Category.objects.all(),
            "products": Product.objects.filter(is_active=True).select_related("category").order_by("category__sort_order", "sort_order", "name"),
        },
    )


def event_solutions(request):
    rows = [
        ("Weddings", "Luxury Wedding Seating for Exceptional Celebrations", "Create an unforgettable wedding experience with premium seating solutions designed for grand weddings, destination celebrations, beach weddings, receptions, and engagement ceremonies. Our collection includes luxury sofas, royal diwans, designer chairs, VIP seating, bridal chairs, and low-rise lounge furniture that complement both traditional and contemporary décor. Thoughtfully curated seating arrangements enhance guest comfort while adding elegance and sophistication to every venue, creating beautiful spaces for ceremonies, photographs, and memorable celebrations.", "event/Weddings.webp", False),
        ("Corporate Events", "Executive Seating Solutions for Professional Gatherings", "Enhance corporate events with premium seating designed for conferences, leadership summits, networking events, annual meetings, award ceremonies, and business gatherings. Our collection features executive chairs, luxury sofas, VIP seating, lounge furniture, diwans, and hospitality seating arrangements that reflect professionalism and excellence. Whether hosting an executive conference or a corporate celebration, our seating solutions create comfortable and distinguished environments that support meaningful interactions, audience engagement, and successful event experiences.", "event/Corporate Events.webp", True),
        ("Product Launches", "Sophisticated Seating for Brand and Product Unveilings", "Make a strong impression with luxury seating solutions for product launches, brand unveilings, media events, investor meetings, and promotional showcases. Our collection includes VIP chairs, designer sofas, contemporary lounge seating, low-rise furniture, and premium diwans that create inviting spaces for guests, media representatives, and stakeholders. Designed to support audience engagement and brand visibility, our seating arrangements contribute to a polished and professional atmosphere that enhances the overall impact of your launch event.", "event/Product Launches.webp", False),
        ("Exhibitions", "Premium Seating Solutions for Exhibitions and Trade Shows", "Create welcoming exhibition spaces with premium seating designed for trade shows, expos, business showcases, and industry events. Our collection includes reception seating, designer chairs, luxury sofas, VIP seating, diwans, and lounge furniture that encourage networking, discussions, and visitor engagement. Comfortable and visually appealing seating areas help enhance attendee experiences while supporting productive business interactions. From exhibition booths to hospitality lounges, our seating solutions contribute to a professional and memorable exhibition environment.", "event/Exhibitions.webp", True),
        ("VIP Lounges", "Exclusive Seating for Distinguished Guests", "Deliver a premium hospitality experience with luxury seating designed for VIP lounges, executive hospitality areas, wedding family lounges, and exclusive guest zones. Our collection features statement sofas, royal diwans, luxury chairs, VIP seating, and low-rise lounge furniture that combine comfort with sophistication. Ideal for weddings, corporate events, exhibitions, and special occasions, these seating solutions create refined environments where distinguished guests can relax, connect, and enjoy an elevated event experience.", "event/VIP Lounges.webp", False),
        ("Special Celebrations", "Elegant Seating for Memorable Occasions", "Add sophistication and comfort to anniversaries, engagement ceremonies, birthday celebrations, cultural events, private gatherings, grand receptions, and festive occasions. Our premium seating collection includes luxury sofas, designer chairs, royal diwans, VIP seating, and stylish lounge furniture designed to complement every celebration. From intimate gatherings to large-scale events, our seating arrangements create inviting spaces that encourage interaction and relaxation while enhancing the visual appeal and atmosphere of the occasion.", "event/Special Celebrations.webp", True),
    ]
    solutions = [
        (title, subtitle, text, "/brand-images/" + quote(image, safe="/"), reverse)
        for title, subtitle, text, image, reverse in rows
    ]
    return render(request, "event_solutions.html", {"solutions": solutions})


def wishlist(request):
    return render(request, "wishlist.html")


def cart(request):
    return render(request, "cart.html")


def contact(request):
    product_name = request.GET.get("product", "")
    quantity = request.GET.get("qty", "")
    prefill = ""
    if product_name:
        prefill = f"I would like a quote for {product_name}"
        if quantity:
            prefill += f" (quantity: {quantity})"
        prefill += "."
    return render(request, "contact.html", {"prefill": prefill})


@require_POST
def contact_submit(request):
    name = (request.POST.get("name") or "").strip()
    email = (request.POST.get("email") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    message = (request.POST.get("message") or "").strip()
    errors = {}
    if not name:
        errors["name"] = "Full Name is required."
    if not email:
        errors["email"] = "Email Address is required."
    elif not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        errors["email"] = "Please enter a valid email address."
    digits = re.sub(r"[\s.-]", "", phone)
    if not phone:
        errors["phone"] = "Phone Number is required."
    elif not re.match(r"^\+?\d{10,14}$", digits):
        errors["phone"] = "Please enter a valid phone number (e.g. +91 9876543210)."
    if not message:
        errors["message"] = "Message is required."
    if errors:
        return JsonResponse({"success": False, "errors": errors, "message": "Please correct the highlighted fields."}, status=400)

    try:
        inquiry = Inquiry.objects.create(name=name, email=email, phone=phone, message=message)
        _save_quote_items(inquiry, request)
    except DatabaseError:
        return JsonResponse(
            {"success": False, "message": "Unable to save this enquiry right now. Please try again in a moment."},
            status=500,
        )
    return JsonResponse(
        {
            "success": True,
            "message": f"Thank you for contacting {settings.SITE_NAME}. We will get back to you shortly.",
        }
    )


def _save_quote_items(inquiry, request):
    raw = (request.POST.get("quote_items") or "").strip()
    try:
        payload = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        payload = []
    if not isinstance(payload, list):
        payload = []
    created = []
    for entry in payload[:30]:
        if not isinstance(entry, dict):
            continue
        slug = (entry.get("slug") or "").strip()
        item_name = (entry.get("name") or "").strip()
        try:
            qty = max(1, min(5000, int(entry.get("qty") or 1)))
        except (TypeError, ValueError):
            qty = 1
        product = Product.objects.filter(slug=slug).first() if slug else None
        if product is None and item_name:
            product = Product.objects.filter(name__iexact=item_name).first()
        if product is None and not item_name:
            continue
        created.append(
            InquiryItem(
                inquiry=inquiry,
                product=product,
                product_name=item_name or (product.name if product else "Item"),
                quantity=qty,
            )
        )
    if created:
        InquiryItem.objects.bulk_create(created)
        inquiry.product = created[0].product
        inquiry.quantity = created[0].quantity
        inquiry.save(update_fields=["product", "quantity"])


def privacy(request):
    return render(request, "legal.html", {"title": "Privacy Policy", "body": "Impress Signature Seating uses the details you submit on the contact form only to reply to your seating enquiry."})


def terms(request):
    return render(request, "legal.html", {"title": "Terms and Conditions", "body": "Quotes are confirmed by the Impress team after an enquiry. Availability changes when a quote is accepted for an event."})

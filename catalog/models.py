import re

from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def shift_qty_text(qty_text, delta):
    text = qty_text or ""
    match = re.search(r"(\d+)", text)
    if not match:
        return str(max(0, int(delta)))
    new_val = max(0, int(match.group(1)) + int(delta))
    return text[: match.start()] + str(new_val) + text[match.end() :]


class Category(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    nav_label = models.CharField(max_length=80)
    subtitle = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=400)
    icon = models.CharField(max_length=80, default="fa-solid fa-chair")
    sort_order = models.PositiveIntegerField(default=0)
    featured_on_home = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Collection"
        verbose_name_plural = "Collections"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("collection", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True, max_length=180)
    image_url = models.CharField(max_length=400)
    size = models.CharField(max_length=160, blank=True)
    qty = models.CharField(max_length=80, blank=True)
    style = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, verbose_name="on website")
    is_rented = models.BooleanField(default=False)
    rented_qty = models.PositiveIntegerField(default=0)
    event_name = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:180]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])

    @property
    def qty_number(self):
        digits = "".join(ch for ch in (self.qty or "") if ch.isdigit())
        return int(digits) if digits else 0

    @property
    def available_units(self):
        return max(0, self.qty_number)

    def rent_units(self, amount, event_name=""):
        amount = max(0, int(amount or 0))
        if amount <= 0:
            return
        self.qty = shift_qty_text(self.qty, -amount)
        self.rented_qty = (self.rented_qty or 0) + amount
        self.is_rented = self.rented_qty > 0
        if event_name:
            self.event_name = event_name
        self.save(update_fields=["qty", "rented_qty", "is_rented", "event_name"])

    def return_units(self, amount=None):
        current = self.rented_qty or 0
        amount = current if amount is None else max(0, int(amount or 0))
        amount = min(amount, current)
        if amount <= 0:
            self.is_rented = False
            self.event_name = ""
            self.save(update_fields=["is_rented", "event_name"])
            return
        self.qty = shift_qty_text(self.qty, amount)
        self.rented_qty = current - amount
        if self.rented_qty <= 0:
            self.rented_qty = 0
            self.is_rented = False
            self.event_name = ""
        else:
            self.is_rented = True
        self.save(update_fields=["qty", "rented_qty", "is_rented", "event_name"])


class Inquiry(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_DECLINED = "declined"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_DECLINED, "Declined"),
        (STATUS_COMPLETED, "Completed"),
    )

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    message = models.TextField()
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    is_read = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer enquiry"
        verbose_name_plural = "Customer enquiries"

    def __str__(self):
        return f"{self.name} · {self.created_at:%d %b %Y}"

    def quote_lines(self):
        items = list(self.items.select_related("product"))
        if items:
            return items
        if self.product_id:
            return [
                InquiryItem(
                    inquiry=self,
                    product=self.product,
                    product_name=str(self.product),
                    quantity=self.quantity or 1,
                )
            ]
        return []

    @transaction.atomic
    def accept(self):
        if self.status == self.STATUS_ACCEPTED:
            return False, "This quote is already accepted."
        if self.status == self.STATUS_COMPLETED:
            return False, "This rental is already complete."
        if self.status == self.STATUS_DECLINED:
            return False, "A declined quote cannot be accepted."
        lines = self.quote_lines()
        if not lines:
            return False, "This quote has no products to move into rented stock."
        for line in lines:
            product = line.product
            qty = int(line.quantity or 1)
            label = line.product_name or (str(product) if product else "this product")
            if product is None:
                return False, f"{label} is no longer in the catalogue."
            if qty > product.qty_number:
                return False, f"Not enough live stock for {product.name}. Available: {product.qty_number}."
        for line in lines:
            line.product.rent_units(int(line.quantity or 1), event_name=self.name)
        self.status = self.STATUS_ACCEPTED
        self.is_read = True
        self.save(update_fields=["status", "is_read"])
        return True, "Quote accepted. Live stock decreased and products added to rented stock."

    @transaction.atomic
    def complete(self):
        if self.status != self.STATUS_ACCEPTED:
            return False, "Only an accepted rental can be marked complete."
        for line in self.items.select_related("product"):
            if line.product_id:
                line.product.return_units(line.quantity or 1)
        self.status = self.STATUS_COMPLETED
        self.completed_at = timezone.now()
        self.is_read = True
        self.save(update_fields=["status", "completed_at", "is_read"])
        return True, "Rental marked complete. Items returned to live stock."

    def decline(self):
        if self.status != self.STATUS_PENDING:
            return False, "Only a pending quote can be declined."
        self.status = self.STATUS_DECLINED
        self.is_read = True
        self.save(update_fields=["status", "is_read"])
        return True, "Quote declined."


class InquiryItem(models.Model):
    inquiry = models.ForeignKey(Inquiry, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=160)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Quoted product"
        verbose_name_plural = "Quoted products"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Category, Inquiry, InquiryItem, Product


class ImpressAdminSite(admin.AdminSite):
    site_header = "Impress Seating Admin"
    site_title = "Impress Admin"
    index_title = "Dashboard"
    site_url = "/"
    enable_nav_sidebar = True
    index_template = "admin/impress_index.html"

    def each_context(self, request):
        context = super().each_context(request)
        context["unread_quotes"] = Inquiry.objects.filter(is_read=False, status=Inquiry.STATUS_PENDING).count()
        return context

    def index(self, request, extra_context=None):
        products = list(Product.objects.all())
        extra_context = extra_context or {}
        extra_context.update(
            {
                "impress_collections": Category.objects.count(),
                "impress_products": len(products),
                "impress_units": sum(product.qty_number for product in products),
                "impress_rented": sum(1 for product in products if product.is_rented),
                "impress_new_quotes": Inquiry.objects.filter(is_read=False, status=Inquiry.STATUS_PENDING).count(),
                "impress_recent": Inquiry.objects.prefetch_related("items")[:8],
            }
        )
        return super().index(request, extra_context)


site = ImpressAdminSite(name="impress_admin")
site.register(User, UserAdmin)
site.register(Group, GroupAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "nav_label", "sort_order", "featured_on_home")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "qty", "rented_qty", "is_rented", "is_active")
    list_filter = ("category", "is_active", "is_rented")
    search_fields = ("name", "size", "style")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("rented_qty", "is_rented", "event_name")


class InquiryItemInline(admin.TabularInline):
    model = InquiryItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "product_name", "quantity")
    fields = ("product_name", "product", "quantity")

    def has_add_permission(self, request, obj=None):
        return False


class InquiryAdmin(admin.ModelAdmin):
    list_display = ("status_badge", "name", "email", "phone", "line_summary", "created_at", "open_link", "action_buttons")
    list_filter = ("status", "is_read", "created_at")
    search_fields = ("name", "email", "phone", "message", "items__product_name")
    readonly_fields = ("name", "email", "phone", "message", "product", "quantity", "status", "created_at", "completed_at")
    inlines = [InquiryItemInline]
    actions = ("accept_quotes", "complete_rentals", "decline_quotes")

    def get_urls(self):
        custom = [
            path("<path:object_id>/accept/", self.admin_site.admin_view(self.accept_view), name="catalog_inquiry_accept"),
            path("<path:object_id>/complete/", self.admin_site.admin_view(self.complete_view), name="catalog_inquiry_complete"),
            path("<path:object_id>/decline/", self.admin_site.admin_view(self.decline_view), name="catalog_inquiry_decline"),
        ]
        return custom + super().get_urls()

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        Inquiry.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.display(description="Status")
    def status_badge(self, obj):
        label = "New" if obj.status == Inquiry.STATUS_PENDING and not obj.is_read else obj.get_status_display()
        return format_html('<span class="impress-pill is-{}">{}</span>', obj.status if obj.is_read or obj.status != "pending" else "new", label)

    @admin.display(description="Products")
    def line_summary(self, obj):
        lines = obj.quote_lines()
        if not lines:
            return "General message"
        return format_html("<br>".join(f"{line.product_name} × {line.quantity}" for line in lines))

    @admin.display(description="")
    def open_link(self, obj):
        url = reverse("impress_admin:catalog_inquiry_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">View</a>', url)

    @admin.display(description="")
    def action_buttons(self, obj):
        if obj.status == Inquiry.STATUS_ACCEPTED:
            url = reverse("impress_admin:catalog_inquiry_complete", args=[obj.pk])
            return format_html('<a class="button" href="{}">Complete</a>', url)
        if obj.status == Inquiry.STATUS_PENDING:
            accept_url = reverse("impress_admin:catalog_inquiry_accept", args=[obj.pk])
            decline_url = reverse("impress_admin:catalog_inquiry_decline", args=[obj.pk])
            return format_html('<a class="button" href="{}">Accept</a> <a class="button" href="{}">Decline</a>', accept_url, decline_url)
        return obj.get_status_display()

    def _run(self, request, object_id, method):
        inquiry = self.get_object(request, unquote(object_id))
        changelist = reverse("impress_admin:catalog_inquiry_changelist")
        if inquiry is None:
            self.message_user(request, "Quote not found.", level=messages.ERROR)
            return HttpResponseRedirect(changelist)
        if request.method != "POST" and request.headers.get("x-requested-with") != "XMLHttpRequest":
            # Dashboard links are GET for a one-click action in this local admin.
            pass
        ok, message = method()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": ok, "message": message}, status=200 if ok else 400)
        self.message_user(request, message, level=messages.SUCCESS if ok else messages.WARNING)
        return HttpResponseRedirect(changelist)

    def accept_view(self, request, object_id):
        inquiry = self.get_object(request, unquote(object_id))
        if inquiry is None:
            return HttpResponseRedirect(reverse("impress_admin:catalog_inquiry_changelist"))
        return self._run(request, object_id, inquiry.accept)

    def complete_view(self, request, object_id):
        inquiry = self.get_object(request, unquote(object_id))
        if inquiry is None:
            return HttpResponseRedirect(reverse("impress_admin:catalog_inquiry_changelist"))
        return self._run(request, object_id, inquiry.complete)

    def decline_view(self, request, object_id):
        inquiry = self.get_object(request, unquote(object_id))
        if inquiry is None:
            return HttpResponseRedirect(reverse("impress_admin:catalog_inquiry_changelist"))
        return self._run(request, object_id, inquiry.decline)

    @admin.action(description="Accept selected quotes")
    def accept_quotes(self, request, queryset):
        done = 0
        for quote in queryset.prefetch_related("items__product"):
            ok, message = quote.accept()
            if ok:
                done += 1
            else:
                self.message_user(request, f"{quote.name}: {message}", level=messages.WARNING)
        if done:
            self.message_user(request, f"{done} quote(s) accepted. Live stock decreased.")

    @admin.action(description="Mark selected rentals complete")
    def complete_rentals(self, request, queryset):
        done = 0
        for quote in queryset.prefetch_related("items__product"):
            ok, message = quote.complete()
            if ok:
                done += 1
            else:
                self.message_user(request, f"{quote.name}: {message}", level=messages.WARNING)
        if done:
            self.message_user(request, f"{done} rental(s) returned to live stock.")

    @admin.action(description="Decline selected quotes")
    def decline_quotes(self, request, queryset):
        done = 0
        for quote in queryset:
            ok, message = quote.decline()
            if ok:
                done += 1
            else:
                self.message_user(request, f"{quote.name}: {message}", level=messages.WARNING)
        if done:
            self.message_user(request, f"{done} quote(s) declined.")


site.register(Category, CategoryAdmin)
site.register(Product, ProductAdmin)
site.register(Inquiry, InquiryAdmin)

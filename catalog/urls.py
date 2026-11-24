from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("collections/<slug:slug>/", views.collection, name="collection"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("event-seating-solutions/", views.event_solutions, name="event_solutions"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("cart/", views.cart, name="cart"),
    path("contact/", views.contact, name="contact"),
    path("contact/submit/", views.contact_submit, name="contact_submit"),
    path("privacy-policy/", views.privacy, name="privacy"),
    path("terms-and-conditions/", views.terms, name="terms"),
]

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

SOFA_CLASSES = {
    "White Single Sofa": "img-white-single",
    "Black Double Sofa": "img-bw-double",
    "White Double Sofa": "img-bw-double",
    "Black Single Sofa": "img-bw-single",
    "Cream Single Sofa": "img-zoom-out-extra",
    "Channel Tufted Backrest Sofa(Red)": "img-zoom-out",
    "Modular channel-tufted Backrest sofa(pink)": "img-zoom-out",
    "Modular channel-tufted Backrest sofa(white)": "img-zoom-out",
}

DIWAN_CLASSES = {
    "Red Modern Velvet Curved Diwan": "img-red-curved-diwan",
    "Yellow Modern Velvet Curved Diwan": "img-curved-diwan",
    "Purple Modern Velvet Curved Diwan": "img-curved-diwan",
    "Blue Modern Velvet Curved Diwan": "img-curved-diwan",
    "Green Modern Velvet Curved Diwan": "img-curved-diwan",
    "Modular Ribbed Velvet Diwan": "img-ribbed-diwan",
    "Modular Ribbed Velvet Diwan (Red)": "img-ribbed-red",
    "Modular Ribbed Velvet Diwan (Blue)": "img-ribbed-blue",
    "Modular Ribbed Velvet Diwan (Green)": "img-ribbed-green",
    "Modular Ribbed Velvet Diwan (Purple)": "img-ribbed-purple",
    "White Diwan": "img-white-diwan",
    "Pallet Diwan": "img-pallet-diwan",
    "Floor Diwan": "img-floor-diwan",
    "Color Diwan": "img-color-diwan",
}


@register.filter
def card_class(product):
    slug = product.category.slug
    if slug == "sofas":
        return SOFA_CLASSES.get(product.name, "")
    if slug == "diwans":
        return DIWAN_CLASSES.get(product.name, "")
    return ""


@register.filter
def sofa_size(value):
    return mark_safe(escape(value or "").replace(" / ", "<br>/ "))

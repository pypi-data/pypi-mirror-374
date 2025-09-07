"""
PicTex Example: E-commerce Product Showcase
Perfect for: Product catalogs, online stores, marketing materials
"""

from pictex import *

# Product data
PRODUCT = {
    "name": "AirPods Pro Max",
    "brand": "Apple",
    "price": "$549",
    "original_price": "$649",
    "rating": 4.8,
    "reviews": 2847,
    "colors": ["Silver", "Space Gray", "Green", "Sky Blue", "Pink"],
    "features": ["Active Noise Cancellation", "Spatial Audio", "20-hour battery"]
}

def create_star_rating(rating: float, max_stars: int = 5) -> Row:
    """Creates a visual star rating"""
    stars = []
    for i in range(max_stars):
        if i < int(rating):
            stars.append(Text("★").color("#FCD34D").font_size(16))
        elif i < rating:  # Half star
            stars.append(Text("☆").color("#FCD34D").font_size(16))
        else:
            stars.append(Text("☆").color("#D1D5DB").font_size(16))
    
    return Row(*stars).gap(2)

def create_color_swatch(color_name: str) -> Column:
    """Creates a color option swatch"""
    color_map = {
        "Silver": "#C0C0C0",
        "Space Gray": "#4A4A4A", 
        "Green": "#4ADE80",
        "Sky Blue": "#38BDF8",
        "Pink": "#FB7185"
    }
    
    swatch = (
        Row()
        .size(24, 24)
        .background_color(color_map.get(color_name, "#9CA3AF"))
        .border_radius("50%")
        .border(2, "#FFFFFF")
        .box_shadows(Shadow(offset=(0, 2), blur_radius=4, color="#00000020"))
    )
    
    label = Text(color_name).font_size(10).color("#6B7280").text_align("center")
    
    return Column(swatch, label).gap(8).horizontal_align("center")

def create_feature_badge(feature: str) -> Row:
    """Creates a feature highlight badge"""
    return (
        Text(feature)
        .font_size(12)
        .color("#1F2937")
        .font_weight(500)
        .padding(8, 12)
        .background_color("#F3F4F6")
        .border_radius(16)
        .border(1, "#E5E7EB")
    )

def create_price_section(price: str, original_price: str) -> Row:
    """Creates the price display with discount"""
    current_price = Text(price).font_size(32).font_weight(700).color("#DC2626")
    
    original = (
        Text(original_price)
        .font_size(18)
        .color("#9CA3AF")
        .text_stroke(1, "#9CA3AF")  # Using text stroke instead of line-through
        .margin(8, 0, 0, 0)
    )
    
    discount_badge = (
        Text("15% OFF")
        .font_size(12)
        .color("white")
        .font_weight(600)
        .padding(4, 8)
        .background_color("#DC2626")
        .border_radius(4)
        .margin(8, 0, 0, 0)
    )
    
    return Row(current_price, original, discount_badge).vertical_align("center").gap(12)

# Product image placeholder (would be actual product image in real scenario)
product_image = (
    Row()
    .size(300, 300)
    .background_color(LinearGradient(["#F8FAFC", "#E2E8F0"]))
    .border_radius(20)
    .border(1, "#E5E7EB")
)

# Product image with "NEW" badge
new_badge = (
    Text("NEW")
    .font_size(10)
    .color("white")
    .font_weight(700)
    .padding(6, 10)
    .background_color("#EF4444")
    .border_radius(12)
    .position(16, 16)  # Top-left corner
)

image_section = Row(product_image, new_badge)

# Product details
brand_name = Text(PRODUCT["brand"]).font_size(14).color("#6B7280").font_weight(500)
product_name = Text(PRODUCT["name"]).font_size(24).font_weight(700).color("#1F2937").margin(4, 0, 0, 0)

# Rating section
rating_stars = create_star_rating(PRODUCT["rating"])
rating_text = Text(f"{PRODUCT['rating']} ({PRODUCT['reviews']} reviews)").font_size(14).color("#6B7280")
rating_section = Row(rating_stars, rating_text).vertical_align("center").gap(8).margin(12, 0)

# Price section
price_section = create_price_section(PRODUCT["price"], PRODUCT["original_price"]).margin(16, 0)

# Color options
color_title = Text("Available Colors").font_size(14).font_weight(600).color("#374151").margin(20, 0, 12, 0)
color_swatches = Row(*[create_color_swatch(color) for color in PRODUCT["colors"]]).gap(16)

# Features
features_title = Text("Key Features").font_size(14).font_weight(600).color("#374151").margin(20, 0, 12, 0)
feature_badges = Column(*[create_feature_badge(feature) for feature in PRODUCT["features"]]).gap(8)

# CTA buttons
add_to_cart_btn = (
    Text("Add to Cart")
    .font_size(16)
    .font_weight(600)
    .color("white")
    .padding(16, 32)
    .background_color("#3B82F6")
    .border_radius(8)
    .text_align("center")
)

buy_now_btn = (
    Text("Buy Now")
    .font_size(16)
    .font_weight(600)
    .color("#3B82F6")
    .padding(16, 32)
    .border(2, "#3B82F6")
    .border_radius(8)
    .text_align("center")
)

cta_section = Row(add_to_cart_btn, buy_now_btn).gap(16).margin(24, 0, 0, 0)

# Product info column
product_info = Column(
    brand_name,
    product_name,
    rating_section,
    price_section,
    color_title,
    color_swatches,
    features_title,
    feature_badges,
    cta_section
).size(width=380)

# Main product layout
product_showcase = Row(
    image_section,
    product_info
).gap(40).vertical_align("top")

# Main container
main_container = (
    Column(product_showcase)
    .padding(40)
    .background_color("white")
    .border_radius(16)
    .box_shadows(Shadow(offset=(0, 4), blur_radius=24, color="#00000015"))
)

# Canvas
canvas = (
    Canvas()
    .font_family("SF Pro Display")
    .background_color(LinearGradient(["#FAFBFC", "#F0F2F5"]))
    .padding(60)
)

canvas.render(main_container).save("product_showcase.png")
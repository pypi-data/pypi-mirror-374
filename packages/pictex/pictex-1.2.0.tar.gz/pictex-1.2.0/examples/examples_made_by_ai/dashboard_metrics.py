"""
PicTex Example: Business Dashboard Metrics Card
Perfect for: KPI dashboards, business reports, analytics visualization
"""

from pictex import *

# Metric data
METRICS = [
    {"title": "Revenue", "value": "$127.4K", "change": "+12.3%", "trend": "up"},
    {"title": "Users", "value": "8,429", "change": "-2.1%", "trend": "down"},
    {"title": "Conversion", "value": "3.24%", "change": "+0.8%", "trend": "up"},
    {"title": "Retention", "value": "87.2%", "change": "+5.2%", "trend": "up"},
]

def create_metric_card(title: str, value: str, change: str, trend: str) -> Column:
    """Creates a modern metric card with trend indicator"""
    
    # Trend icon and color
    trend_icon = "📈" if trend == "up" else "📉"
    trend_color = "#10B981" if trend == "up" else "#EF4444"
    
    # Header with title and trend icon
    header = Row(
        Text(title).font_size(14).color("#64748B").font_weight(500),
        Text(trend_icon).font_size(16)
    ).horizontal_distribution("space-between").vertical_align("center")
    
    # Main value
    main_value = Text(value).font_size(32).font_weight(700).color("#1E293B").margin(8, 0)
    
    # Change indicator
    change_text = Text(change).font_size(14).color(trend_color).font_weight(600)
    change_label = Text("from last month").font_size(12).color("#94A3B8")
    change_row = Row(change_text, change_label).gap(8).vertical_align("center")
    
    # Card container
    card = (
        Column(header, main_value, change_row)
        .padding(24)
        .background_color("white")
        .border_radius(12)
        .border(1, "#E2E8F0")
        .box_shadows(Shadow(offset=(0, 1), blur_radius=3, color="#0000001A"))
        .gap(4)
    )
    
    return card

def create_progress_bar(percentage: float, color: str = "#3B82F6") -> Column:
    """Creates a progress bar visualization"""
    bar_width = 200
    fill_width = int(bar_width * percentage / 100)
    
    # Progress bar background
    bg_bar = Row().size(bar_width, 8).background_color("#E5E7EB").border_radius(4)
    
    # Progress fill
    fill_bar = Row().size(fill_width, 8).background_color(color).border_radius(4)
    
    # Progress text
    progress_text = Text(f"{percentage}% Complete").font_size(12).color("#6B7280")
    
    return Column(
        Row(bg_bar, fill_bar.position(0, 0)),  # Layered bars
        progress_text
    )

# Create metric cards
metric_cards = []
for i, metric in enumerate(METRICS):
    card = create_metric_card(**metric)
    metric_cards.append(card)

# Grid layout (2x2)
row1 = Row(metric_cards[0], metric_cards[1]).gap(20)
row2 = Row(metric_cards[2], metric_cards[3]).gap(20)

# Add progress section
progress_section = Column(
    Text("Monthly Goals Progress").font_size(18).font_weight(600).color("#1E293B").margin(0, 0, 16, 0),
    Column(
        create_progress_bar(73, "#10B981"),
        create_progress_bar(45, "#F59E0B"),
        create_progress_bar(89, "#3B82F6"),
    ).gap(8)
).padding(24).background_color("white").border_radius(12).border(1, "#E2E8F0")

# Dashboard title
dashboard_title = Column(
    Text("Business Dashboard").font_size(28).font_weight(700).color("#1E293B"),
    Text("Real-time metrics and KPIs").font_size(16).color("#64748B")
).gap(4).margin(0, 0, 32, 0)

# Complete dashboard
dashboard = Column(
    dashboard_title,
    Column(row1, row2).gap(20),
    progress_section
).gap(32)

# Canvas with subtle background
canvas = (
    Canvas()
    .font_family("Inter")
    .background_color(LinearGradient(["#F8FAFC", "#F1F5F9"]))
    .padding(40)
)

canvas.render(dashboard).save("dashboard_metrics.png")
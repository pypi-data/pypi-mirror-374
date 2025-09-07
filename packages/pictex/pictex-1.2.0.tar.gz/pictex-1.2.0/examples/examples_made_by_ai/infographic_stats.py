from pictex import *

# Data for the infographic
STATS_DATA = {
    "frameworks": [
        {"name": "Django", "percentage": 45, "color": "#0C4B33"},
        {"name": "Flask", "percentage": 38, "color": "#000000"},
        {"name": "FastAPI", "percentage": 31, "color": "#009688"},
        {"name": "Pandas", "percentage": 67, "color": "#150458"},
    ],
}

def create_horizontal_bar_chart(items: list) -> Column:
    """Creates horizontal bar chart for frameworks"""
    bars = []
    max_width = 300
    
    for item in items:
        # Calculate bar width
        bar_width = int((item["percentage"] / 100) * max_width)
        
        # Framework name
        name_text = Text(item["name"]).font_size(14).font_weight(600).color("#374151")
        
        # Percentage text
        perc_text = Text(f"{item['percentage']}%").font_size(14).font_weight(700).color(item["color"])
        
        # Bar background
        bar_bg = Row().size(max_width, 24).background_color("#F1F5F9").border_radius(12)
        
        # Bar fill
        bar_fill = (
            Row()
            .size(bar_width, 24)
            .background_color(item["color"])
            .border_radius(12)
        )
        
        # Bar container with overlay
        bar_container = Row(bar_bg, bar_fill.position(0, 0))
        
        # Complete bar row
        bar_row = Row(
            name_text.size(width=100),
            bar_container,
            perc_text.size(width=50)
        ).vertical_align("center").gap(16)
        
        bars.append(bar_row)
    
    return Column(*bars).gap(12)

def create_section_header(title: str, subtitle: str = None) -> Column:
    """Creates a section header with title and optional subtitle"""
    title_text = Text(title).font_size(24).font_weight(700).color("#1E293B")
    
    if subtitle:
        subtitle_text = Text(subtitle).font_size(16).color("#64748B").margin(4, 0, 0, 0)
        return Column(title_text, subtitle_text).gap(4)
    
    return Column(title_text)

# Frameworks section
frameworks_header = create_section_header("Most Popular Frameworks", "Usage percentage among survey respondents").margin(0, 0, 24, 0)
frameworks_chart = create_horizontal_bar_chart(STATS_DATA["frameworks"])
frameworks_section = Column(frameworks_header, frameworks_chart)

# Main content layout
content = frameworks_section.padding(50).background_color("white").border_radius(20).box_shadows(
    Shadow(offset=(0, 4), blur_radius=24, color="#00000015")
)

# Canvas
canvas = (
    Canvas()
    .background_color(LinearGradient(["#F8FAFC", "#F1F5F9"]))
    .padding(40)
)

canvas.render(content, crop_mode=CropMode.CONTENT_BOX).save("infographic_stats.png")
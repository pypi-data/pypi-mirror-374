"""
PicTex Example: Professional Certificate Template  
Perfect for: Course completion, awards, achievements, diplomas
"""

from pictex import *

# Certificate data
CERTIFICATE = {
    "title": "Certificate of Completion",
    "subtitle": "This certifies that",
    "recipient_name": "Alex Johnson",
    "course_name": "Advanced Python Programming",
    "description": "has successfully completed the comprehensive course and demonstrated proficiency in advanced Python concepts including decorators, metaclasses, async programming, and software architecture patterns.",
    "completion_date": "December 15, 2024",
    "instructor": "Dr. Sarah Mitchell",
    "organization": "TechAcademy Institute",
    "certificate_id": "CERT-2024-PY-ADV-001247"
}

def create_decorative_border() -> Column:
    """Creates an elegant decorative border"""
    # Corner decorative elements
    corner_size = 60
    
    # Top-left corner
    top_left = (
        Row()
        .size(corner_size, corner_size)
        .background_color("#C9A96E")
        .border_radius(0, 0, corner_size, 0)
        .position(0, 0)
    )
    
    # Top-right corner  
    top_right = (
        Row()
        .size(corner_size, corner_size)
        .background_color("#C9A96E")
        .border_radius(0, 0, 0, corner_size)
        .position(740, 0)
    )
    
    # Bottom-left corner
    bottom_left = (
        Row()
        .size(corner_size, corner_size)
        .background_color("#C9A96E")
        .border_radius(0, corner_size, 0, 0)
        .position(0, 540)
    )
    
    # Bottom-right corner
    bottom_right = (
        Row()
        .size(corner_size, corner_size)
        .background_color("#C9A96E")
        .border_radius(corner_size, 0, 0, 0)
        .position(740, 540)
    )
    
    return Column(top_left, top_right, bottom_left, bottom_right)

def create_ornamental_divider() -> Row:
    """Creates decorative divider elements"""
    # Central ornamental element
    center_ornament = Text("◆").font_size(16).color("#C9A96E")
    
    # Side lines
    left_line = Row().size(80, 1).background_color("#C9A96E")
    right_line = Row().size(80, 1).background_color("#C9A96E")
    
    return Row(
        left_line,
        center_ornament,
        right_line
    ).vertical_align("center").gap(20).horizontal_distribution("center")

def create_signature_line(name: str, title: str) -> Column:
    """Creates a signature line with name and title"""
    # Signature line
    signature_line = Row().size(200, 1).background_color("#666666")
    
    # Name and title
    name_text = Text(name).font_size(14).font_weight(600).color("#333333")
    title_text = Text(title).font_size(12).color("#666666")
    
    return Column(
        signature_line,
        name_text,
        title_text
    ).gap(8).horizontal_align("center")

# Main certificate background
certificate_bg = (
    Row()
    .size(800, 600)
    .background_color("#FDFDF9")
    .border(8, LinearGradient(["#C9A96E", "#B8956A"]))
    .border_radius(12)
)

# Decorative borders
decorative_border = create_decorative_border()

# Header section
header_title = (
    Text(CERTIFICATE["title"])
    .font_size(36)
    .font_weight(800)
    .color("#2C5F7C")
    .text_align("center")
    .margin(60, 0, 20, 0)
)

# Organization name  
org_name = (
    Text(CERTIFICATE["organization"])
    .font_size(18)
    .font_weight(600)
    .color("#C9A96E")
    .text_align("center")
    .margin(0, 0, 30, 0)
)

# Subtitle
subtitle = (
    Text(CERTIFICATE["subtitle"])
    .font_size(16)
    .color("#666666")
    .text_align("center")
)

# Recipient name (large and prominent)
recipient_name = (
    Text(CERTIFICATE["recipient_name"])
    .font_size(48)
    .font_weight(700)
    .color("#2C5F7C")
    .text_align("center")
    .margin(20, 0)
)

# Decorative divider
divider = create_ornamental_divider().margin(20, 0)

# Course information
course_completion = Text("has successfully completed").font_size(16).color("#666666").text_align("center")
course_name = (
    Text(CERTIFICATE["course_name"])
    .font_size(24)
    .font_weight(700)
    .color("#2C5F7C")
    .text_align("center")
    .margin(10, 0)
)

# Description
description = (
    Text(CERTIFICATE["description"])
    .font_size(14)
    .color("#555555")
    .text_align("center")
    .line_height(1.5)
    .padding(0, 80)
    .margin(20, 0)
)

# Date and signatures section
completion_date = (
    Text(f"Completed on {CERTIFICATE['completion_date']}")
    .font_size(14)
    .color("#666666")
    .text_align("center")
    .margin(30, 0, 40, 0)
)

# Signatures
instructor_signature = create_signature_line(CERTIFICATE["instructor"], "Course Instructor")

signature_section = Row(
    instructor_signature,
).horizontal_distribution("space-around").vertical_align("center").margin(20, 0, 40, 0)

# Certificate ID
cert_id = (
    Text(f"Certificate ID: {CERTIFICATE['certificate_id']}")
    .font_size(10)
    .color("#999999")
    .text_align("center")
)

# Main content layout
content = Column(
    header_title,
    org_name,
    subtitle,
    recipient_name,
    divider,
    course_completion,
    course_name,
    description,
    completion_date,
    signature_section,
    cert_id
).horizontal_align("center")

# Complete certificate
certificate = Row(
    certificate_bg.position(0, 0),
    decorative_border.position(0, 0),
    content.size(800)
)

# Canvas
canvas = (
    Canvas()
    .font_family("Georgia")  # Serif font for formal look
    .background_color(LinearGradient(["#F8F9FA", "#E9ECEF"]))
    .padding(50)
)

canvas.render(certificate).save("certificate_template.png")
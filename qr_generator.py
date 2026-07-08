import streamlit as st
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw
from io import BytesIO
import re

st.set_page_config(page_title="Branded QR Code Generator", layout="centered")

st.title("Branded QR Code Generator")

def valid_hex(value):
    return bool(re.fullmatch(r"#[0-9A-Fa-f]{6}", value))

url = st.text_input("Website URL", "https://www.example.com/")
qr_colour = st.text_input("QR Code Colour", "#343434")
border_colour = st.text_input("Border Colour", "#00447A")
logo_file = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg", "webp"])

border_thickness = st.slider("Border Thickness", 10, 60, 26)
border_radius = st.slider("Border Radius", 10, 80, 42)
logo_size_percent = st.slider("Logo Size", 10, 28, 20)
logo_padding = st.slider("White Space Around Logo", 10, 50, 28)
gap = st.slider("Gap Between QR Code and Border", 10, 60, 24)

generate = st.button("Generate QR Code")

if generate:
    if not url:
        st.error("Please enter a website URL.")
    elif not valid_hex(qr_colour) or not valid_hex(border_colour):
        st.error("Please enter valid hex colours, for example #343434.")
    else:
        qr = qrcode.QRCode(
            error_correction=ERROR_CORRECT_H,
            box_size=20,
            border=2
        )
        qr.add_data(url)
        qr.make(fit=True)

        qr_img = qr.make_image(
            fill_color=qr_colour,
            back_color="white"
        ).convert("RGBA")

        w, h = qr_img.size

        canvas_size = w + 2 * (gap + border_thickness)
        canvas = Image.new("RGBA", (canvas_size, canvas_size), "white")
        draw = ImageDraw.Draw(canvas)

        draw.rounded_rectangle(
            (0, 0, canvas_size - 1, canvas_size - 1),
            radius=border_radius,
            outline=border_colour,
            width=border_thickness,
            fill="white"
        )

        qr_position = (gap + border_thickness, gap + border_thickness)
        canvas.paste(qr_img, qr_position, qr_img)

        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            target_size = int(w * (logo_size_percent / 100))
            logo.thumbnail((target_size, target_size))

            cx = canvas_size // 2
            cy = canvas_size // 2
            circle_radius = max(logo.size) // 2 + logo_padding

            draw.ellipse(
                (
                    cx - circle_radius,
                    cy - circle_radius,
                    cx + circle_radius,
                    cy + circle_radius
                ),
                fill="white"
            )

            logo_x = cx - logo.size[0] // 2
            logo_y = cy - logo.size[1] // 2
            canvas.alpha_composite(logo, (logo_x, logo_y))

        st.image(canvas, caption="QR Code Preview")

        buffer = BytesIO()
        canvas.save(buffer, format="PNG")
        buffer.seek(0)

        st.download_button(
            label="Download PNG",
            data=buffer,
            file_name="branded_qr_code.png",
            mime="image/png"
        )
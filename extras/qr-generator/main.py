import qrcode
from PIL import ImageDraw

scale = 3

qr_code = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10 * scale
)

qr_code.add_data("https://reg.sfintra.net/")
qr_code.make()

qr_image = qr_code.make_image(fill_color="black", back_color="white").convert("RGB")

draw = ImageDraw.Draw(qr_image)

w, h = qr_image.size

# White logo background
draw.rounded_rectangle(
    (w / 2 - 60 * scale, h / 2 - 30 * scale, w / 2 + 60 * scale, h / 2 + 30 * scale),
    radius=10,
    outline="black",
    fill="white",
    width=5,
)

# Black circle
draw.ellipse(
    (
        w / 2 - 22 * scale - 23 * scale,
        h / 2 - 22 * scale,
        w / 2 + 22 * scale - 23 * scale,
        h / 2 + 22 * scale,
    ),
    fill="black",
)

# Black square
draw.rectangle(
    (
        w / 2 - 20 * scale + 23 * scale,
        h / 2 - 20 * scale,
        w / 2 + 20 * scale + 23 * scale,
        h / 2 + 20 * scale,
    ),
    fill="black",
)

# save the QR code generated
qr_image.save("sf-reg-url-qr.png")

print("QR code generated!")

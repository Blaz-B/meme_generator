from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, render_template_string
from io import BytesIO
import base64

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<body>
  <h2>Meme Generator</h2>

  <form method="POST" enctype="multipart/form-data">
    <label>Naloži sliko:</label><br>
    <input type="file" name="img" required><br><br>

    <label>Top Text:</label><br>
    <input type="text" name="topText"><br><br>

    <label>Bottom Text:</label><br>
    <input type="text" name="bottomText"><br><br>

    <button type="submit">Ustvari</button>
  </form>

  {% if img_data %}
  <img src="data:image/png;base64,{{ img_data }}">
  {% endif %}
</body>
</html>
"""
PADDING = 20
FONT_PATH = "fonts/roboto.ttf"

def generateImage(img, topText, bottomText):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    fontSize = 20
    font = ImageFont.truetype(FONT_PATH, fontSize)
    bbox = draw.textbbox((0,0), topText, font=font)
    text_w = bbox[2]-bbox[0]
    text_h = bbox[3]-bbox[1]

    if text_h > h//2 - PADDING:
        fontSize = int(fontSize * ((h//2 - PADDING)/text_h))
        font = ImageFont.truetype(FONT_PATH, fontSize)
        bbox = draw.textbbox((0,0), topText, font=font)
        text_w = bbox[2]-bbox[0]

    x = (w - text_w)//2
    y = PADDING
    draw.text((x,y), topText, font=font, fill="white", stroke_width=2, stroke_fill="black")

    fontSize = 20
    font = ImageFont.truetype(FONT_PATH, fontSize)
    bbox = draw.textbbox((0,0), bottomText, font=font)
    text_w = bbox[2]-bbox[0]
    text_h = bbox[3]-bbox[1]

    if text_h > h//2 - PADDING:
        fontSize = int(fontSize * ((h//2 - PADDING)/text_h))
        font = ImageFont.truetype(FONT_PATH, fontSize)
        bbox = draw.textbbox((0,0), bottomText, font=font)
        text_w = bbox[2]-bbox[0]
        text_h = bbox[3]-bbox[1]

    x = (w - text_w)//2
    y = h - text_h - PADDING
    draw.text((x,y), bottomText, font=font, fill="white", stroke_width=2, stroke_fill="black")

    return img

@app.route("/", methods=["GET","POST"])
def index():
    img_data = None

    if request.method == "POST":
        file = request.files["img"]
        topText = request.form.get("topText", "")
        bottomText = request.form.get("bottomText", "")

        img = Image.open(file.stream).convert("RGB")
        img = generateImage(img, topText, bottomText)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_data = base64.b64encode(buffer.getvalue()).decode()

    return render_template_string(HTML, img_data=img_data)

if __name__ == "__main__":
    app.run(debug=True)

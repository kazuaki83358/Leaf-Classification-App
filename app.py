from flask import Flask, render_template, request
import torch
from torchvision import models, transforms
from PIL import Image
from classes import leaf_classes
import pandas as pd
import io, base64

app = Flask(__name__)

# ------------------------------------
# Load Model
# ------------------------------------
num_classes = len(leaf_classes)
model = models.mobilenet_v2()
model.classifier[1] = torch.nn.Linear(model.last_channel, num_classes)

model.load_state_dict(torch.load("leaf_model_update.pth", map_location="cpu"))
model.eval()

# ------------------------------------
# Load CSV With Leaf Information
# ------------------------------------
leaf_df = pd.read_csv("leaves_info.csv")  # ← place your CSV in the same folder as app.py
leaf_info = leaf_df.set_index("English Name").to_dict(orient="index")

# ------------------------------------
# Image Transform (same as training)
# ------------------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],   # ImageNet mean
        [0.229, 0.224, 0.225]    # ImageNet std
    )
])

# ------------------------------------
# Prediction Function
# ------------------------------------
def predict(img):
    img = img.convert("RGB")
    tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)
        probs = torch.nn.functional.softmax(output[0], dim=0)
        confidence, predicted = torch.max(probs, 0)

    leaf_name = leaf_classes[predicted.item()]
    confidence_val = float(confidence.item()) * 100

    # Fetch details from CSV
    details = leaf_info.get(leaf_name, {
        "Hindi Name": "Not Available",
        "Medicinal/General Uses": "No data",
        "Pros": "No data",
        "Cons": "No data",
    })

    return leaf_name, confidence_val, details

# ------------------------------------
# Convert image to Base64 for display
# ------------------------------------
def img_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# ------------------------------------
# Main Route
# ------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    confidence = None
    details = None
    uploaded_img = None

    if request.method == "POST":
        file = request.files.get("image")
        if file:
            img = Image.open(file.stream)
            prediction, confidence, details = predict(img)
            uploaded_img = img_to_base64(img)

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        details=details,
        uploaded_img=uploaded_img
    )

# ------------------------------------
# Start App
# ------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)

import json
import os
from functools import lru_cache

import numpy as np
from PIL import Image
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "rice_leaf_disease_model.keras")
CLASS_NAMES_PATH = os.path.join(PROJECT_ROOT, "models", "class_names.json")

DISEASE_INFO = {
    "bacterial_leaf_blight": {
        "label": "Bacterial Leaf Blight",
        "description": "Bacterial leaf blight is a bacterial disease that causes yellowing, water-soaked lesions, and leaf blight symptoms, often spreading through rain and contaminated tools.",
        "solution": "Use clean disease-free seeds, remove infected plant debris, avoid overhead watering, and apply a copper-based bactericide or recommended agricultural bactericide as advised by local extension services."
    },
    "brown_spot": {
        "label": "Brown Spot",
        "description": "Brown spot is a common fungal disease that produces brown lesions with yellow halos on rice leaves and can reduce grain quality and yield.",
        "solution": "Improve field sanitation, reduce excess nitrogen, avoid water stress, remove infected residue, and use a recommended fungicide such as tricyclazole or propiconazole when advised by an agronomist."
    },
    "healthy": {
        "label": "Healthy",
        "description": "No disease detected. The leaf appears healthy and does not show signs of infection.",
        "solution": "Continue regular crop management, balanced nutrition, and proper irrigation to keep the crop healthy."
    },
    "leaf_blast": {
        "label": "Leaf Blast",
        "description": "Leaf blast is a fungal disease causing spindle-shaped or diamond-shaped lesions on leaves, often becoming more severe under high humidity and warm weather.",
        "solution": "Plant resistant varieties, reduce excessive nitrogen, remove infected residue, and use recommended fungicides such as tricyclazole or azoxystrobin when necessary."
    },
    "leaf_scald": {
        "label": "Leaf Scald",
        "description": "Leaf scald creates pale or bleached, scald-like lesions on leaves and may spread quickly in wet conditions.",
        "solution": "Improve drainage, remove infected plant residues, avoid overcrowding, and apply a recommended fungicide or copper-based treatment as advised by agricultural guidance."
    },
    "narrow_brown_spot": {
        "label": "Narrow Brown Spot",
        "description": "Narrow brown spot causes narrow dark brown lesions along leaves and is often favored by high humidity and poor field sanitation.",
        "solution": "Use balanced fertilization, remove infected crop debris, manage water efficiently, and apply a recommended fungicide according to local crop protection advice."
    }
}


@lru_cache(maxsize=1)
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    return tf.keras.models.load_model(MODEL_PATH)


def load_class_names():
    if not os.path.exists(CLASS_NAMES_PATH):
        raise FileNotFoundError(f"Class names file not found: {CLASS_NAMES_PATH}")

    with open(CLASS_NAMES_PATH, "r") as file:
        return json.load(file)


def get_disease_details(label):
    normalized_label = str(label).strip()
    if normalized_label in DISEASE_INFO:
        return DISEASE_INFO[normalized_label]

    fallback = {
        "label": normalized_label.replace("_", " ").title(),
        "description": "This disease has been detected. Please consult a local agricultural expert for a precise diagnosis and treatment plan.",
        "solution": "Follow local crop protection guidance, remove infected parts, and apply the recommended treatment for this disease."
    }
    return fallback


def preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((224, 224))
    image_array = np.asarray(image, dtype=np.float32) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array


def predict_image(image_path):
    model = load_model()
    class_names = load_class_names()

    image_array = preprocess_image(image_path)
    prediction = model.predict(image_array, verbose=0)[0]

    predicted_index = int(np.argmax(prediction))
    predicted_label = class_names[predicted_index]
    confidence = float(prediction[predicted_index])
    disease_info = get_disease_details(predicted_label)

    return {
        "label": predicted_label,
        "disease": disease_info["label"],
        "description": disease_info["description"],
        "solution": disease_info["solution"],
        "confidence": confidence
    }

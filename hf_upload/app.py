import os
import sys

import gradio as gr

# Reuse the same model code as the Flask backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from model import predict_image  # noqa: E402


def classify(image_path):
    if image_path is None:
        return "Please upload a rice leaf image."

    try:
        result = predict_image(image_path)
    except Exception as exc:
        return f"Error: {exc}"

    confidence = float(result["confidence"]) * 100

    solution = result["solution"]
    if isinstance(solution, (list, tuple)):
        solution = "\n".join(f"- {item}" for item in solution)

    return (
        f"## {result['disease']}\n\n"
        f"**Confidence:** {confidence:.2f}%\n\n"
        f"**About:** {result['description']}\n\n"
        f"**Suggested solution:**\n\n{solution}"
    )


demo = gr.Interface(
    fn=classify,
    inputs=gr.Image(type="filepath", label="Upload a rice leaf image"),
    outputs=gr.Markdown(label="Result"),
    title="LeafGuard - Rice Leaf Disease Detection",
    description="Upload a photo of a rice leaf and the CNN model will detect the disease and suggest a treatment.",
)

if __name__ == "__main__":
    demo.launch()

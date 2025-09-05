import os
import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
import importlib.resources as pkg_resources


def MSE(y_true, y_pred):
    """Custom metric for model loading."""
    return tf.reduce_mean(tf.square(y_true - y_pred))


def calculate_reconstruction_error(original, reconstructed):
    """Compute reconstruction error for anomaly detection."""
    return 1 / np.mean(np.square(original - reconstructed), axis=(1, 2, 3))


def get_resource_path(filename: str) -> str:
    """Get the path of a bundled resource file inside the package."""
    return str(pkg_resources.files("ai_isometric_extractor") / filename)


def run_inference(
    img_path,
    output_dir=None,
    yolo_model_path=None,
    anomaly_model_path=None,
    recon_model_path=None,
    threshold=0.014581064133542713,
):
    """
    Run isometric image detection & reconstruction.

    Parameters
    ----------
    img_path : str
        Path to input image.
    output_dir : str, optional
        If provided, cleaned images will be saved here.
    yolo_model_path : str, optional
        Path to custom YOLO model (default: bundled best.pt).
    anomaly_model_path : str, optional
        Path to custom anomaly detection model (default: bundled anomaly.keras).
    recon_model_path : str, optional
        Path to custom reconstruction model (default: bundled my_model_keras.keras).
    threshold : float
        Threshold for reconstruction error to classify isometric images.

    Returns
    -------
    list of np.ndarray
        Cleaned image arrays (uint8).
    """

    # Locate bundled models if custom paths not given
    if yolo_model_path is None:
        yolo_model_path = get_resource_path("best.pt")
    if anomaly_model_path is None:
        anomaly_model_path = get_resource_path("anomaly.keras")
    if recon_model_path is None:
        recon_model_path = get_resource_path("my_model_keras.keras")

    # Load models
    yolo_model = YOLO(yolo_model_path)
    model_constraint = tf.keras.models.load_model(anomaly_model_path)
    model1 = tf.keras.models.load_model(recon_model_path, custom_objects={"MSE": MSE})

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Load image
    img = cv2.imread(img_path)
    results = yolo_model(img)

    cleaned_images = []

    for i, result in enumerate(results[0].boxes.xyxy):
        x_min, y_min, x_max, y_max = map(int, result)
        cropped_img = img[y_min:y_max, x_min:x_max]
        cropped_img = cv2.resize(cropped_img, (224, 224))
        cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2GRAY)
        cropped_img = np.expand_dims(cropped_img, axis=0)

        check = model_constraint.predict(cropped_img)
        error_recon = calculate_reconstruction_error(cropped_img, check)

        print("Reconstruction Error For Input Image:", error_recon)

        if error_recon < threshold:
            print("Isometric Image Successfully Detected")
            cleaned = model1.predict(cropped_img / 255.0)

            cleaned_img = (cleaned[0] * 255).astype(np.uint8)
            if cleaned_img.ndim == 3 and cleaned_img.shape[-1] == 1:
                cleaned_img = cleaned_img.squeeze(-1)

            cleaned_images.append(cleaned_img)

            if output_dir:
                save_path = os.path.join(output_dir, f"cleaned_{i}.jpg")
                cv2.imwrite(save_path, cleaned_img)
                print(f"Saved cleaned image to {save_path}")

        else:
            print("Non-Isometric Image Detected")

    return cleaned_images

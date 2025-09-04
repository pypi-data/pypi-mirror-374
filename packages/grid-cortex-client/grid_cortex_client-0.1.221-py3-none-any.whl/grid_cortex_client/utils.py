from io import BytesIO
import base64
import os
from typing import Union

import numpy as np
import requests
from PIL import Image, ImageDraw


def encode_image(image):
    """Reads and encodes an image to a base64 string."""
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def image_to_base64(image_input: Union[str, Image.Image, np.ndarray]) -> str:
    """
    Converts an image from various formats (path, PIL, numpy) to a base64 string.
    """
    if isinstance(image_input, str):
        # It's a file path or URL
        if os.path.exists(image_input):
            image = Image.open(image_input).convert("RGB")
        else: # Assuming it's a URL
            response = requests.get(image_input)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGB")
    elif isinstance(image_input, np.ndarray):
        image = Image.fromarray(image_input.astype('uint8'), 'RGB')
    elif isinstance(image_input, Image.Image):
        image = image_input.convert("RGB")
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def decode_base64_to_array(encoded_string: str) -> np.ndarray:
    """
    Decodes a base64 string that represents a NumPy array's raw bytes.
    The calling function is expected to know the dtype and shape.
    """
    decoded_bytes = base64.b64decode(encoded_string)
    # Attempt to decode as float32, which is common for keypoints
    try:
        return np.frombuffer(decoded_bytes, dtype=np.float32)
    except ValueError:
        # Fallback for other types like int64 for matches
        return np.frombuffer(decoded_bytes, dtype=np.int64)

def visualize_matches(
    image0: Image.Image,
    image1: Image.Image,
    points0: np.ndarray,
    points1: np.ndarray,
    save_path: str = "matches_visualization.png",
) -> None:
    """
    Draws lines between corresponding keypoints on two images and saves the result.
    """
    # Ensure images are RGB
    image0 = image0.convert("RGB")
    image1 = image1.convert("RGB")

    # Create a new image with space for both images side-by-side
    width = image0.width + image1.width
    height = max(image0.height, image1.height)
    combined_image = Image.new("RGB", (width, height))
    combined_image.paste(image0, (0, 0))
    combined_image.paste(image1, (image0.width, 0))

    draw = ImageDraw.Draw(combined_image)

    # Adjust points1 coordinates for the combined image
    points1_adj = points1.copy()
    points1_adj[:, 0] += image0.width

    # Draw lines for matches
    for p0, p1_adj in zip(points0, points1_adj):
        draw.line((p0[0], p0[1], p1_adj[0], p1_adj[1]), fill="cyan", width=2)

    # Draw keypoints
    for p0 in points0:
        draw.ellipse((p0[0]-2, p0[1]-2, p0[0]+2, p0[1]+2), fill="magenta")
    for p1_adj in points1_adj:
        draw.ellipse((p1_adj[0]-2, p1_adj[1]-2, p1_adj[0]+2, p1_adj[1]+2), fill="magenta")

    if save_path:
        combined_image.save(save_path)
        print(f"Saved visualization to {save_path}")
    else:
        combined_image.show()
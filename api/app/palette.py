from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image, ImageOps
from sklearn.cluster import KMeans


@dataclass(frozen=True)
class ExtractedColor:
    red: int
    green: int
    blue: int
    percentage: float

    @property
    def hex(self) -> str:
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"


def extract_palette(
    image_bytes: bytes, color_count: int
) -> tuple[int, int, list[ExtractedColor]]:
    """Return the most common K-means clusters in an image held in memory."""
    with Image.open(BytesIO(image_bytes)) as source:
        source = ImageOps.exif_transpose(source)
        original_width, original_height = source.size
        image = source.convert("RGB")
        image.thumbnail((200, 200))
        pixels = np.asarray(image, dtype=np.uint8).reshape(-1, 3)

    unique_color_count = len(np.unique(pixels, axis=0))
    cluster_count = min(color_count, len(pixels), unique_color_count)
    if cluster_count == 0:
        raise ValueError("La imagen no contiene píxeles.")

    model = KMeans(n_clusters=cluster_count, n_init=10, random_state=42)
    labels = model.fit_predict(pixels)
    centers = np.rint(model.cluster_centers_).clip(0, 255).astype(int)

    counts = np.bincount(labels, minlength=cluster_count)
    percentages = counts / counts.sum() * 100
    order = np.argsort(percentages)[::-1]

    return original_width, original_height, [
        ExtractedColor(
            red=int(centers[index][0]),
            green=int(centers[index][1]),
            blue=int(centers[index][2]),
            percentage=round(float(percentages[index]), 1),
        )
        for index in order
    ]

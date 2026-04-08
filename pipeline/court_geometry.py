import csv
import cv2
import os
import numpy as np
import json
import sys
from typing import Tuple, Union

COURT_DIMENSIONS = (9.0, 18.0)
HALE_CSV = "hale.csv"


def load_hale(csv_path: str, hall_id: str) -> np.ndarray:
    with open(csv_path) as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if row["id"] == hall_id:
                return np.array([
                    [float(row["x1"]), float(row["y1"])],
                    [float(row["x2"]), float(row["y2"])],
                    [float(row["x3"]), float(row["y3"])],
                    [float(row["x4"]), float(row["y4"])],
                ], dtype=np.float32)

    raise ValueError(f"Hala '{hall_id}' nie znaleziona w {csv_path}")


class VolleyballCourt:
    def __init__(self, img_points: np.ndarray):
        self.width, self.length = COURT_DIMENSIONS

        real_pts = np.array([
            [0.0, 0.0],
            [self.width, 0.0],
            [self.width, self.length],
            [0.0, self.length],
        ], dtype=np.float32)

        self.H, _ = cv2.findHomography(img_points, real_pts)

    def image_to_metric(self, x: float, y: float) -> Tuple[float, float]:
        pt = np.array([[[x, y]]], dtype=np.float32)
        xm, ym = cv2.perspectiveTransform(pt, self.H)[0][0]
        return float(xm), float(self.length - ym)

    def classify_zone(self, x: float, y: float, court_side: str):

        if court_side == "down":
            if y < 9.0:
                return "BLAD"
            y_eff = y - 9.0
        else:
            if y > 9.0:
                return "BLAD"
            y_eff = 9.0 - y 

        if x < 0 or x > self.width or y < 0 or y > self.length:
            return "OUT"

        if y_eff < 3.0:
            zones = [4, 3, 2] if court_side == "down" else [2, 3, 4]
        else:
            zones = [5, 6, 1] if court_side == "down" else [1, 6, 5]

        if x < 3.0:
            return zones[0]
        elif x < 6.0:
            return zones[1]
        else:
            return zones[2]



JSONL_PATH = "serves.jsonl"

def load_court_side_from_jsonl(serve_name: str) -> str:
    with open(JSONL_PATH, "r") as f:
        for line in f:
            record = json.loads(line)
            if record.get("id") == serve_name:
                return record.get("court_side")

    raise ValueError(f"Serve {serve_name} not found in JSONL.")


def process_contact_from_jsonl(serve_name: str, court: VolleyballCourt, court_side: str):
    jsonl_path = "serves.jsonl"
    updated_records = []
    found = False

    with open(jsonl_path, "r") as f:
        for line in f:
            record = json.loads(line)

            if record.get("id") == serve_name:
                found = True

                if "player_contact" in record:
                    contact_data = record["player_contact"]
                elif "contact" in record:
                    contact_data = record["contact"]
                else:
                    print("No contact data found.")
                    return

                x_img = float(contact_data["x_img"])
                y_img = float(contact_data["y_img"])
                source = contact_data.get("source", "contact")

                x_m, y_m = court.image_to_metric(x_img, y_img)
                zone = court.classify_zone(x_m, y_m, court_side)

                print("=== RESULT ===")
                print(f"Source:       {source}")
                print(f"Image Coords: ({x_img:.1f}, {y_img:.1f}) px")
                print(f"Real Coords:  ({x_m:.2f}, {y_m:.2f}) m")
                print(f"Court side:   {court_side}")
                print(f"ZONE:         {zone}")

                record["result"] = {
                    "x_img": round(x_img, 3),
                    "y_img": round(y_img, 3),
                    "x_m": round(x_m, 3),
                    "y_m": round(y_m, 3),
                    "zone": zone
                }

            updated_records.append(record)

    if not found:
        print(f"Serve {serve_name} not found.")
        return

    with open(jsonl_path, "w") as f:
        for r in updated_records:
            f.write(json.dumps(r) + "\n")

    print("Result zapisany do JSONL.")


def run_court_geometry(
    serve_name: str,
    hall_id: str
):
    img_points = load_hale(HALE_CSV, hall_id)
    court = VolleyballCourt(img_points)

    court_side = load_court_side_from_jsonl(serve_name)

    process_contact_from_jsonl(serve_name, court, court_side)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Użycie: python court_geometry.py serve_XXXX hala_id")
        sys.exit(1)

    run_court_geometry(sys.argv[1], sys.argv[2])

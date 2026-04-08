from pathlib import Path
import cv2
import os
from trim_video import run_trim_video
from extract_frames import extract_frames
from predict_yolo import predict_yolo_serve
from filtr import run_yolo_filter
from predict_sam2 import run_sam2
from geometria_predict import run_contact_detection
from detect_player_contact import run_player_contact_analysis
from court_geometry import run_court_geometry
from make_vis_video import run_make_vis_video

import time
import csv

BASE_DIR = Path(__file__).resolve().parent
RAW_VIDEO_DIR = BASE_DIR / "data/raw_videos/serves"
FRAMES_DIR = BASE_DIR / "data/frames"
YOLO_RUNS_DIR = BASE_DIR / "runs/detect"

def get_best_imgsz(serve_name: str) -> int:
    """
    Dobiera dynamicznie imgsz na podstawie pierwszej klatki.
    """
    target_dir = FRAMES_DIR / serve_name

    if not target_dir.exists():
        return 1280

    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp")

    for file in os.listdir(target_dir):
        if file.lower().endswith(valid_extensions):
            img_path = target_dir / file
            img = cv2.imread(str(img_path))
            if img is not None:
                h, w = img.shape[:2]
                return max(h, w)

    return 1280

def run_pipeline(
    serve_name: str,
    hall_id: str,
    visualize: bool = False, 
    make_video: bool = False, 
    progress_callback=None
):

    steps = 8
    current = 0
    
    def update():
        nonlocal current
        current += 1
        if progress_callback:
            progress_callback(int(current / steps * 100))
    print(f"\n=== PIPELINE DLA: {serve_name} (hala: {hall_id}) ===")

    video_path = RAW_VIDEO_DIR / f"{serve_name}.mp4"

    if not video_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku wideo: {video_path}")

    # 0. Przycinanie wideo
    print("Przycinanie wideo...")
    run_trim_video(str(video_path))
    update()

    # 1. Ekstrakcja klatek
    print("Ekstrakcja klatek...")
    extract_frames(serve_name)
    update()

    # 2. YOLO
    dynamic_imgsz = get_best_imgsz(serve_name)
    print(f"Detekcja piłki (YOLO) imgsz={dynamic_imgsz}...")
    predict_yolo_serve(serve_name, hall_id, img_size=dynamic_imgsz)
    update()

    # 3. Filtracja YOLO
    labels_dir = YOLO_RUNS_DIR / f"predict_{serve_name}" / "labels"
    print("Filtrowanie detekcji YOLO...")
    run_yolo_filter(str(labels_dir))
    update()

    # 4. SAM2 tracking
    print("Tracking piłki (SAM2)...")
    run_sam2(serve_name, visualize=visualize)
    update()

    # 5. Detekcja kontaktu
    print("Detekcja kontaktu...")
    run_contact_detection(serve_name)
    update()

    # 6. Detekcja zawodnika

    print("Detekcja zawodnika...")
    run_player_contact_analysis(serve_name, hall_id)
    update()

    # 7. Homografia + klasyfikacja strefy
    print("Homografia boiska...")
    run_court_geometry(serve_name, hall_id)
    update()

    # 8. Tworzenie wideo wizualizacji
    if make_video:
        print("Tworzenie filmu wizualizacji...")
        run_make_vis_video(serve_name)
        update()

    print("\nPIPELINE ZAKOŃCZONY")
        
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Użycie:")
        print("python pipeline.py serve_XXXX hala_id")
        sys.exit(1)

    try:
        run_pipeline(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(f"Błąd: {e}")
        sys.exit(1)

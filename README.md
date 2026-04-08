# 🏐 Volleyball Serve Analyzer

## 🎥 Demo

![Demo](demo/demo.mp4)

The system detects the ball, tracks its trajectory, identifies the receiving player, and classifies the landing zone on the court.

---

## 📌 Opis projektu

Projekt przedstawia system do automatycznej analizy pojedynczej zagrywki w piłce siatkowej na podstawie nagrania wideo z nieruchomej kamery. System umożliwia pełną rekonstrukcję zdarzenia — od detekcji i śledzenia piłki, przez wykrycie momentu kontaktu, aż po identyfikację zawodnika przyjmującego oraz klasyfikację miejsca upadku piłki do stref boiska.

Rozwiązanie zostało zaprojektowane jako modularny pipeline przetwarzania wideo, niezależny od interfejsu użytkownika, umożliwiający zarówno analizę wsadową, jak i interaktywną.

---

## 📌 Project Overview

This project implements a system for automatic analysis of a single volleyball serve based on video recorded from a static camera. The system reconstructs the full event pipeline — from ball detection and tracking, through contact detection, to identifying the receiving player and classifying the landing zone on the court.

The solution is designed as a modular video processing pipeline, independent from the user interface, supporting both batch and interactive execution.

---

## 🏗 Architektura / Architecture

**Backend (warstwa obliczeniowa / processing layer)**

- pełne przetwarzanie wideo i analiza zdarzeń
- uruchamianie z CLI lub GUI
- niezależność od interfejsu

**Frontend (GUI)**

- aplikacja desktopowa (PySide6 / Qt)
- wybór nagrania i hali
- konfiguracja analizy
- wizualizacja wyników

---

## 🔁 Pipeline przetwarzania / Processing Pipeline

1. **Preprocessing**
   - przycinanie nagrania
   - ekstrakcja klatek (FFmpeg)
   - mechanizm cache

2. **Detekcja piłki (YOLOv8)**
   - model trenowany do wykrywania piłki
   - wysoka rozdzielczość wejścia
   - filtrowanie detekcji

3. **Śledzenie piłki (SAM2)**
   - inicjalizacja maski
   - propagacja między klatkami
   - odporność na utratę detekcji

4. **Analiza trajektorii**
   - analiza prędkości i kierunku
   - detekcja kontaktu

5. **Detekcja zawodnika**
   - YOLO (person)
   - filtracja względem boiska

6. **Analiza przestrzenna**
   - homografia
   - klasyfikacja strefy

---

## 🤖 Wykorzystane technologie / Technologies

- Python
- YOLOv8 (Ultralytics) – detekcja obiektów
- SAM2 – segmentacja i tracking
- OpenCV – przetwarzanie obrazu
- FFmpeg – przetwarzanie wideo
- PySide6 (Qt) – interfejs użytkownika

---

## 📐 Geometria boiska / Court Geometry

- konfiguracja w `hale.csv`
- 4 punkty referencyjne
- homografia i analiza przestrzenna

---

## 📦 Wyniki / Output

Wyniki zapisywane są w pliku:

## serves.jsonl

Każdy rekord zawiera:

- trajektorię piłki
- moment kontaktu
- stronę boiska
- zawodnika
- współrzędne (px + metry)
- strefę lub błąd

---

## 🎯 Najważniejsze cechy / Key Features

- modularna architektura
- odporność na błędy detekcji
- analiza oparta na fizyce ruchu
- separacja backendu i GUI
- tryb wsadowy i interaktywny

---

## ⚠️ Models

Model weights are not included in the repository.

Please download:

- YOLOv8 weights
- SAM2 checkpoint

and place them in the `models/` directory.

# Eksperymentalny lektor RapidOCR dla GameOpti

## Co zrobiliśmy?

Dodaliśmy alternatywny silnik OCR oparty na RapidOCR PP-OCRv6
i ONNX Runtime, ponieważ oryginalny Tesseract miał problemy
z rozpoznawaniem dialogów w Wolfensteinie przez GeForce NOW.

## Wyniki testów

- Fedora 44, Intel i7-3740QM (bez AVX2).
- RapidOCR poprawnie rozpoznaje dialogi postaci.
- Szybki tryb bez detektora: średnio 82 ms na klatkę.
- Działa istniejące tłumaczenie i polski głos Piper.
- Poprawiliśmy akceptowanie dialogów i ograniczyliśmy powtórzenia.

## Co powinien zrobić deweloper?

1. Przejrzeć zmiany w narrator_ocr.py i narrator_pipeline.py.
2. Zintegrować RapidOCR jako opcjonalny silnik obok Tesseract.
3. Przenieść eksperymentalny serwer RapidOCR do docelowej
   architektury aplikacji.
4. Dodać automatyczne wykrywanie obszaru dialogów.
5. Sprawdzić deduplikację, poprawność tłumaczeń i opóźnienia.
6. Zachować dotychczasowe działanie Tesseract jako domyślne.

## Ważne

To prototyp działający w Wolfensteinie, a nie gotowa
implementacja dla wszystkich gier.

RapidOCR jest aktywowany zmienną GAMEOPTI_RAPIDOCR=1.
Serwer nasłuchuje lokalnie na 127.0.0.1:8765 i wymaga
osobnego środowiska Python 3.12.

Prosimy o przegląd kodu i samodzielne dostosowanie rozwiązania
do architektury głównego projektu.

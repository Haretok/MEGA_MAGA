# CV/ML Дизайн и пайплайн

## 1. CV/ML задачи
1. **Face Detection & Alignment**: RetinaFace / YOLOV8-face (crop & align 112x112).
2. **Quality Assessment**: Оценка размытия (Laplacian variance), освещенности и occlusion (маски, очки).
3. **Liveness / Anti-Spoofing**: Silent Liveness (RGB + NIR инфракрасная камера).
4. **Feature Extraction**: ArcFace / InsightFace (ResNet-50 / MobileFaceNet, 512D embedding).
5. **Matching**: HNSW ANN-поиск (Cosine Similarity) по локальному индексу.

## 2. Verification vs Identification
На проходной используется **Identification (1-to-Many)** по базе сотрудников кампуса. Для ускорения используется ANN HNSW индекс, обеспечивающий sub-millisecond поиск по сотням тысяч лиц.

## 3. Выбор порогов принятий решений
* `Score >= 0.85`: `ALLOW` (автоматическое открытие).
* `0.60 <= Score < 0.85`: `MANUAL_REVIEW` (передача охране).
* `Score < 0.60`: `DENY` (отказ в доступе).

## 4. Почему LLM здесь не нужен
LLM не место на горячем пути принятия решений `allow/deny` из-за высокой задержки (latency > 1-2 сек), детерминированных требований безопасности и риска галлюцинаций. Логика decision engine строится строго на детерминированных правилах и thresholds.

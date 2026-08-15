# Целевая архитектура системы

## 1. Компоненты и распределение Edge / Cloud
* **Edge Node (на каждой проходной)**:
  * GPU-сервер (например, NVIDIA Jetson / RTX).
  * Задачи: Capture -> Quality Check -> Liveness -> Embedding Extraction -> HNSW Search (локальный кеш) -> Decision Engine -> Команда турникету.
* **Central Cloud / ЦОД**:
  * База сотрудников и биометрических шаблонов, генерация HNSW-индекса.
  * Центральный Audit Log, асинхронный синк событий.
  * UI для рабочего места охраны (manual review).

## 2. Схема потока данных (Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    participant C as Камера (RTSP)
    participant E as Edge Node (GPU)
    participant T as Контроллер турникета
    participant G as UI Охраны
    participant S as Центральный сервер

    C->>E: Поток кадров
    E->>E: Детекция + Quality Check + Liveness
    alt Качество низкое или Spoof
        E->>T: Команда: КЛОЗЕД (Keep Closed)
        E->>G: Событие -> Manual Review (Low Quality/Spoof)
        E->>S: Sync Audit Event (Async)
    else Quality & Liveness OK
        E->>E: Поиск вектора в локальном HNSW-кеше
        alt Score >= 0.85 (High Confidence)
            E->>T: Команда: OPEN
            E->>S: Sync Audit Event (Async)
        else 0.60 <= Score < 0.85 (Low Margin)
            E->>T: Команда: КЛОЗЕД
            E->>G: Alert -> Manual Review
            E->>S: Sync Audit Event (Async)
        else Score < 0.60
            E->>T: Команда: DENY
            E->>S: Sync Audit Event (Async)
        end
    end





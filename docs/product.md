# Целевая архитектура системы

## 1. Компоненты и распределение Edge / Cloud
* **Edge Node (на каждой проходной)**:
  * GPU-сервер (например, NVIDIA Jetson / RTX)[cite: 1].
  * Задачи: Capture -> Quality Check -> Liveness -> Embedding Extraction -> HNSW Search (локальный кеш) -> Decision Engine -> Команда турникету[cite: 1].
* **Central Cloud / ЦОД**:
  * База сотрудников и биометрических шаблонов, генерация HNSW-индекса[cite: 1].
  * Центральный Audit Log, асинхронный синк событий[cite: 1].
  * UI для рабочего места охраны (manual review)[cite: 1].

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
        E->>T: Команда: КЛОЗЕД (Keep Closed)[cite: 1]
        E->>G: Событие -> Manual Review (Low Quality/Spoof)[cite: 1]
        E->>S: Sync Audit Event (Async)[cite: 1]
    else Quality & Liveness OK
        E->>E: Поиск вектора в локальном HNSW-кеше[cite: 1]
        alt Score >= 0.85 (High Confidence)
            E->>T: Команда: OPEN[cite: 1]
            E->>S: Sync Audit Event (Async)[cite: 1]
        else 0.60 <= Score < 0.85 (Low Margin)
            E->>T: Команда: КЛОЗЕД[cite: 1]
            E->>G: Alert -> Manual Review[cite: 1]
            E->>S: Sync Audit Event (Async)[cite: 1]
        else Score < 0.60
            E->>T: Команда: DENY[cite: 1]
            E->>S: Sync Audit Event (Async)[cite: 1]
        end
    end

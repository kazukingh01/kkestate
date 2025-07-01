# Purpose

Cleaning data to analyze it efficiently.

# Schedule

see: [crontab](../others/crontab)

# Script

```bash
python process_estate.py stats
python process_estate.py mapping --sample 10000 --unique # --update
python process_estate.py process # --update
python generate_detail_ref.py stats
python generate_detail_ref.py process --limit 500 # --update 
```

# Workflow

```mermaid
flowchart LR
  %% Processes
  subgraph Processes["Processes"]
    P1["クレンジングマスタ整備"]
    P2["データクレンジング"]
    P3["同一値補完処理"]
  end

  %% Tables
  subgraph Tables["Tables"]
    T1["estate_mst_key"]
    T2["estate_detail"]
    T3["estate_run"]
    T4["estate_mst_cleaned"]
    T5["estate_cleaned"]
    T6["estate_detail_ref"]
  end

  %% Edges
  P1 --- |SELECT| T1
  P1 --- |SELECT| T2
  P1 --> |DELETE/INSERT| T4
  P1 --> |UPDATE| T1

  P2 --- |SELECT| T2
  P2 --- |SELECT| T3
  P2 --- |SELECT| T4
  P2 --> |DELETE/INSERT| T5

  P3 --- |SELECT| T2
  P3 --- |SELECT| T3
  P3 --> |DELETE/INSERT| T6

  %% Styling
  classDef process fill:#bbdefb,stroke:#0d47a1,stroke-width:2px;
  classDef table   fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px;

  class P1,P2,P3 process;
  class T1,T2,T3,T4,T5,T6 table;
```
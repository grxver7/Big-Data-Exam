# Big Data Docker Setup für die MTG-Datenpipeline

## Einführung
Diese Anleitung bietet detaillierte Schritte zur Einrichtung einer Big Data-Pipeline-Umgebung mit Docker. Die Pipeline besteht aus mehreren wichtigen Komponenten: Apache Hadoop, Apache Airflow, PostgreSQL und einem Webserver auf Basis von Node.js, die alle innerhalb von Docker-Containern orchestriert werden. Diese Einrichtung ist darauf ausgelegt, Daten von der Magic: The Gathering API (https://docs.magicthegathering.io/) zu verarbeiten und zu speichern.

## Aufgabenbeschreibung
Das Ziel ist es, diese Daten zu nutzen, um eine durchsuchbare Datenbank aller MTG-Handelskarten zu erstellen.

Workflow:
- Daten von api.magicthegathering.io sammeln
- Rohdaten (JSON-Dateien) in HDFS speichern
- Rohdaten optimieren, reduzieren und bereinigen und in ein endgültiges Verzeichnis in HDFS speichern
- MTG-Daten in eine Endbenutzerdatenbank (z. B. MySQL, MongoDB) exportieren
- Eine einfache HTML-Oberfläche bereitstellen, die:
  - aus der Endbenutzerdatenbank liest
  - Benutzereingaben (Kartennamen, Text oder Künstler) verarbeitet
  - Suchergebnisse anzeigt
- Der gesamte Datenworkflow muss innerhalb eines ETL-Workflow-Tools (z. B. Pentaho Data Integration oder Airflow) implementiert und automatisch ausgeführt werden.

## Setup-Anweisungen für den ETL-Workflow:
Dieser Abschnitt erklärt, wie der Workflow eingerichtet wird.

### # Docker installieren:
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER # Logout und Login erneut durchführen
```

### # Erstellen eines Docker-Netzwerks
Um ein benutzerdefiniertes Docker-Netzwerk zu erstellen, das die Kommunikation zwischen den Containern ermöglicht, verwenden Sie den folgenden Befehl:
```bash
docker network create --driver bridge bigdatanet
```

### # Docker-Images herunterladen
Laden Sie die notwendigen Docker-Images für Hadoop, Airflow, PostgreSQL und den Webserver (Node.js) herunter:

1. Hadoop-Image:
```bash
docker pull marcelmittelstaedt/spark_base:latest
```

2. Airflow-Image:
```bash
docker pull marcelmittelstaedt/airflow:latest
```

3. PostgreSQL-Image:
Version: psql (PostgreSQL) 17.1 (Debian 17.1-1.pgdg120+1)
```bash
docker pull postgres
```

4. Webserver (Node.js):
Version: v22.11.0
```bash
docker pull node
```

### # Docker-Container starten
Starten Sie die Docker-Container für Hadoop, Airflow, PostgreSQL und den Webserver. Jede Komponente läuft in ihrem eigenen Container.

1. Hadoop:
```bash
docker run -dit --name hadoop \
  -p 8088:8088 -p 9870:9870 -p 9864:9864 -p 10000:10000 \
  -p 8032:8032 -p 8030:8030 -p 8031:8031 -p 9000:9000 -p 8888:8888 \
  --net bigdatanet marcelmittelstaedt/spark_base:latest
```

2. Airflow:
```bash
docker run -dit --name airflow \
  -p 8080:8080 \
  --net bigdatanet marcelmittelstaedt/airflow:latest
```

3. PostgreSQL:
```bash
docker run --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -d --network bigdatanet postgres
```
Der Postgres-Docker-Container ist nun so eingerichtet, dass er über das Docker-Netzwerk "bigdatanet" kommunizieren kann und verwendet das Passwort "admin" zur Authentifizierung.

4. Webserver (Node.js): Der Webserver wird später empfohlen.

### # Dateien abrufen
Klonen Sie das Repository und kopieren Sie die notwendigen Skripte in die jeweiligen Docker-Container.

1. Repository klonen:
```bash
git clone https://github.com/grxver7/Big-Data-Exam.git
```

2. Verzeichnis für die Website erstellen:
```bash
mkdir website_mtg
```

3. Dateien an den richtigen Ort kopieren:

- Python-Skripte in den Airflow-Container kopieren:
```bash
for file in /home/lxcx_holder/Big-Data-Exam/python_scripts/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/python/; done
```

- DAGs in den Airflow-Container kopieren:
```bash
for file in /home/lxcx_holder/Big-Data-Exam/DAG/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/dags/; done
```

- Website-Dateien in den Webserver kopieren:
```bash
for file in /home/lxcx_holder/Big-Data-Exam/website_mtg/*; do
    cp "$file" /home/lxcx_holder/website_mtg/; done
```

### # Dienste anpassen und starten

1. **Hadoop:**
   Melden Sie sich im Hadoop-Container an und starten Sie die Hadoop-Dienste:
```bash
docker exec -it hadoop bash
sudo su hadoop
cd
start-all.sh
hiveserver2
```

2. **Airflow:**
   Melden Sie sich im Airflow-Container an, installieren Sie die notwendigen Python-Abhängigkeiten und greifen Sie auf die Airflow-UI zu:
```bash
sudo docker exec -it airflow bash
sudo su airflow
pip install mtgsdk
```
   Greifen Sie auf Airflow zu unter: [http://<external-ip-of-vm>:8080/admin/](http://<external-ip-of-vm>:8080/admin/)

### # Webserver einrichten
Verwenden Sie das Dockerfile im Verzeichnis website_mtg, um den Node.js-basierten Webserver zu erstellen.

1. Docker-Image erstellen:
```bash
sudo docker build -t mtg-node-app .
```

2. Den Webserver-Container starten:
```bash
docker run -it -p 5000:5000 --net bigdatanet --name mtg-node-app mtg-node-app
```
Der Webserver-Docker-Container ist nun auf Port 5000 zugänglich und kann über das Docker-Netzwerk "bigdatanet" kommunizieren.

### # Fehlerbehebung
- **Airflow ist nicht zugänglich?** Versuchen Sie, die VM oder Ihr lokales Gerät neu zu starten.
- **Container kommunizieren nicht?** Stellen Sie sicher, dass alle Container mit dem Netzwerk `bigdatanet` verbunden sind.

### # Eindrücke der implementierten Website
Nun sind die Karten zur Suche unter http://<external-ip-of-vm>:5000/ verfügbar.

![image](https://github.com/user-attachments/assets/0e3892b8-da1e-4932-9120-8f3461bdb8d3)

Die Bilder sind anklickbar:

![image](https://github.com/user-attachments/assets/19f36be5-0723-4c04-91d5-18bca935e85a)

# Weitere Informationen zum Workflow

### # ETL-Workflow
Das folgende Diagramm zeigt den ETL-Workflow des Prüfungsprojekts. Der Workflow basiert auf dem Konzept der Medallion-Architektur, mit einer schrittweisen Aufbereitung der Daten durch die Bronze/Silver/Gold-Ebenen. Dies vereinfacht unter anderem die Umsetzung des ETL-Workflows (indem der ETL-Prozess in Phasen unterteilt wird, was auch das Debuggen und Warten erleichtert), erhöht die Datenqualität (jede Ebene verbessert die Daten mit unterschiedlichen Aufgaben und Zielen) und verbessert die Nachvollziehbarkeit der Daten (korrupten Daten in höheren Ebenen können mit den Daten in niedrigeren Ebenen verglichen werden).
Im Kontext des Projekts wurde eine zusätzliche Raw-Ebene eingeführt, in der die Daten zuerst als JSON im HDFS gespeichert werden, wie es im Prüfungsprojekt erforderlich ist. Die Gold-Ebene wird in Form einer PostgreSQL-Datenbank implementiert und enthält nur die für das Reporting erforderlichen Datensätze: card_id, name, text, artist, image_url. Die Daten werden dann für die Verwendung auf einer Website bereitgestellt, die mit Node.js (auf einem Docker-Container) gehostet wird.

![image](https://github.com/user-attachments/assets/753503cc-eaa6-46c0-85f1-19f9f4992040)

### # Batch-Prozess
Die Implementierung des ETL-Workflows funktioniert als Batch-Prozess, der alle MTG-Kartendaten auf einmal lädt, was einige Zeit in Anspruch nehmen kann. Das Bild unten veranschaulicht die erwartete Dauer jedes Prozesses im DAG.

![image](https://github.com/user-attachments/assets/84139c69-c33c-435f-b831-6d936f10160b)

### # DAG
Der Workflow wird mit Airflow automatisiert, mit den folgenden Schritten im DAG:

![image](https://github.com/user-attachments/assets/87203bda-a907-4ee9-9f10-6422efcfe56b)

1. Zunächst müssen die Verzeichnisse erstellt werden (create_hdfs_raw_dir_task, create_hdfs_bronze_dir_task, create_hdfs_silver_dir_task), um sicherzustellen, dass die HDFS-Verzeichnisse für die Datenspeicherung vorhanden sind.
2. Reinigung und Hochladen der Daten: Sobald die Verzeichnisse erstellt sind, wird das alte Rohdatenmaterial gelöscht (delete_old_data_task), neue Daten in HDFS hochgeladen (upload_to_hdfs_task) und dann verarbeitet (collect_job_mtg).
3. Datenverarbeitung in Schichten: Die Daten fließen von der Raw-Schicht (über collect_job_mtg) in die Bronze-Schicht (bronze_job_mtg), dann in die Silver-Schicht (silver_job_mtg) und schließlich in eine PostgreSQL-Datenbank (ingestDB_job_mtg).

### # Job-Beschreibung
Die Tabelle beschreibt jeden Job im DAG:

| Job Name                  | Beschreibung                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| create_hdfs_bronze_directory | Erstellt das Verzeichnis für die Bronze-Schicht im HDFS.                       |
| create_hdfs_silver_directory | Erstellt das Verzeichnis für die Silver-Schicht im HDFS.                       |
| create_raw_directory       | Erstellt ein lokales Verzeichnis für die temporäre Speicherung der Rohdaten.                  |
| create_hdfs_raw_directory  | Erstellt das HDFS-Verzeichnis für die temporäre Speicherung der Rohdaten.                               |
| clear_local_raw_dir        | Löscht das lokale Verzeichnis für Rohdaten, um Platz für neue Daten zu schaffen.           |
| upload_to_hdfs             | Simuliert das Hochladen von Daten in HDFS (DummyOperator).                                        |
| collect_job_mtg            | Sammelt Magic: The Gathering-Daten von der API, speichert sie als JSON-Datei lokal und lädt sie in HDFS hoch.       |
| bronze_job_mtg             | Wandelt die Rohdaten im JSON-Format in Parquet für die Bronze-Schicht in HDFS um.    |
| silver_job_mtg             | Transformiert die Bronze-Schicht-Daten in eine 3NF-Struktur, um Redundanzen und Anomalien zu reduzieren.   |
| ingestDB_job_mtg           | Lädt die bereinigten Daten in eine PostgreSQL-Datenbank. |

# # Der Datensatz
Eine ausführlichere Beschreibung der Daten findet sich in der ergänzenden PDF-Datei mit dem Titel „Doku_Datenstruktur_&_Datensammlung.pdf“.

### # Beispiel-Daten aus der Silber-Ebene (3NF)

*5 rows of 'cards' table:*
| *card_id*                            | *name*           | *mana_cost* | *cmc* | *type*                  | *rarity* | *text*                      | *power* | *toughness* | *artist*               | *image_url*     | *set* | *set_name*              |
|----------------------------------------|--------------------|---------------|---------|---------------------------|------------|-------------------------------|-----------|---------------|--------------------------|-------------------|---------|---------------------------|
| 72290bcf-54c4-594...                   | Llanowar Elves     | {G}           | 1.0     | Creature — Elf Druid      | Common     | {T}: Add {G}.                 | 1         | 1             | Victor Adame Minguez     | null              | PANA    | MTG Arena Promos          |
| 331efc27-0224-5da...                   | Vessel of Volatility| {1}{R}        | 2.0     | Enchantment              | Common     | {1}{R}, Sacrifice...         | null      | null          | Kieran Yanner            | http://gatherer...| SOI     | Shadows over Innistrad    |
| 06d0520e-9ecf-592...                   | Taii Wakeen, Perf...| {R}{W}        | 2.0     | Legendary Creature — Elf  | Rare       | Whenever a source...         | 2         | 3             | David Auden Nash         | null              | POTJ    | Outlaws of Thunder...     |
| c6dfe188-fe59-589...                   | Swamp              | null          | 0.0     | Basic Land — Swamp       | Common     | ({T}: Add {B}.)              | null      | null          | Svetlin Velinov          | http://gatherer...| ELD     | Throne of Eldraine        |
| 0d57455f-8257-50c...                   | Ingenious Mastery  | {X}{2}{U}     | 3.0     | Sorcery                  | Rare       | You may pay {2}{U}...       | null      | null          | Cristi Balanescu         | null              | PSTX    | Strixhaven: School...     |

---

*5 rows of 'foreign_names' table:*
| *card_id*                            | *foreign_name*     | *language*   | *foreign_text*                                | *foreign_type*           | *flavor*              | *foreign_image_url*  |
|----------------------------------------|----------------------|----------------|-------------------------------------------------|----------------------------|-------------------------|------------------------|
| 41007287-4046-58f...                   | Tirapúas trasgo      | Spanish        | {R}, {T}: El Tirapúa...                         | Criatura — Chamán Goblin   | La senda de un chamán...| http://gatherer.w...   |
| 84efda29-4924-5aa...                   | 石の予見者、デネソール  | Japanese       | 石の予見者、デネソールが戦場に出た...              | 伝説のクリーチャー — 人間・貴族 | 「おぬしは戦場で一日は勝利を得るか...| http://gatherer.w...   |
| 7643e6ce-358e-5c9...                   | 震惧军将莉莲娜      | Chinese Simplified | 每当一个由你操控的生物死去时，抓一...           | 传奇鹏洛客 — 莉莲娜         | null                    | http://gatherer.w...   |
| 7f32d840-982c-566...                   | Duelliste de l'es... | French         | Vol, vigilance La...                            | Créature — humain...       | Nathan Steuer, ch...     | http://gatherer.w...   |
| 48a6fc46-d0f4-51d...                   | Technicien de gad... | French         | Quand le Technici...                            | Créature — gobelin         | null                    | http://gatherer.w...   |

---

### *5 rows of 'legalities' table:*
| *card_id*                            | *format*  | *legality* |
|----------------------------------------|------------|--------------|
| 24fa27de-5f37-5b6...                   | Oathbreaker| Legal        |
| 81bfed24-7596-57f...                   | Alchemy    | Legal        |
| ce3fd22d-f477-568...                   | Predh      | Legal        |
| a3599f7e-e36b-5bf...                   | Legacy     | Legal        |
| ab2f6dcd-8ed0-561...                   | Vintage    | Legal        |

---

*5 rows of 'printings' table:*
| *card_id*                            | *set_code* |
|----------------------------------------|--------------|
| 96cf6577-a58f-5c4...                   | J21          |
| 3d416628-6961-537...                   | PRM          |
| a4f7d689-45d9-568...                   | AKH          |
| 9ac9bceb-4766-5de...                   | HBG          |
| 5bf11981-a6f8-534...                   | RNA          |

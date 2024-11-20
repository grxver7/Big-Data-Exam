# Big Data Docker Setup für die MTG-Datenpipeline

## 1. Einführung
Diese Anleitung beschreibt die detaillierten Schritte zur Einrichtung einer Big-Data-Pipeline-Umgebung mit Docker. Die Pipeline umfasst mehrere Komponenten: Apache Hadoop, Apache Airflow, PostgreSQL und einen Webserver auf Basis von Node.js, die alle innerhalb von Docker-Containern orchestriert werden. Diese Einrichtung ist darauf ausgelegt, eine Magic: The Gathering (MTG)-Datenpipeline zu verarbeiten.

## 2. Einrichtung der Datenpipeline für MTG-Daten:

### # Docker installieren:
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER # Melde dich ab und wieder an
```

### # Docker-Netzwerk erstellen
Erstelle ein benutzerdefiniertes Netzwerk für die Container:
```bash
docker network create --driver bridge bigdatanet
```

### # Docker-Images ziehen
Lade die notwendigen Docker-Images für Hadoop, Airflow, PostgreSQL und den Webserver (Node.js) herunter:

1. Hadoop-Image:
```bash
docker pull marcelmittelstaedt/spark_base:latest
```

2. Airflow-Image:
```bash
docker pull marcelmittelstaedt/airflow:latest
```

3. PostgreSQL-Image:
```bash
docker pull postgres
```

4. Webserver (Node.js):
```bash
docker pull node
```

### # Docker-Container starten
Starte die Docker-Container für Hadoop, Airflow, PostgreSQL und den Webserver. Jede Komponente wird in ihrem eigenen Container ausgeführt.

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

4. Webserver (Node.js): Implementierung erst später empfohlen

### # Dateien holen
Klone das Repository und kopiere die notwendigen Skripte in die jeweiligen Docker-Container.

1. Repository klonen:
```bash
git clone https://github.com/grxver7/Big-Data-Exam.git
```

2. Verzeichnis für die Website erstellen:
```bash
mkdir website_mtg
```

3. Dateien in die richtige Umgebung kopieren:

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

### # Dienste konfigurieren und starten

1. **Hadoop:**
   Melde dich im Hadoop-Container an und starte die Hadoop-Dienste:
```bash
docker exec -it hadoop bash
sudo su hadoop
cd
start-all.sh
hiveserver2
```

2. **Airflow:**
   Melde dich im Airflow-Container an, installiere die erforderlichen Python-Abhängigkeiten und greife auf das Airflow-Dashboard zu:
```bash
sudo docker exec -it airflow bash
sudo su airflow
pip install mtgsdk
```
   Greife auf Airflow zu unter: [http://<external-ip-of-vm>:8080/admin/](http://<external-ip-of-vm>:8080/admin/)

### # Webserver einrichten
Verwende das Dockerfile im Verzeichnis `website_mtg`, um den Webserver auf Basis von Node.js zu erstellen.

1. Docker-Image erstellen:
```bash
sudo docker build --no-cache -t mtg-node-app .
```
   oder
```bash
sudo docker build -t mtg-node-app .
```

2. Webserver-Container starten:
```bash
docker run -it -p 5000:5000 --net bigdatanet --name mtg-node-app mtg-node-app
```

### # Fehlerbehebung
- **Airflow ist nicht zugänglich?** Versuche, die VM oder deinen lokalen Rechner neu zu starten.
- **Container können nicht miteinander kommunizieren?** Stelle sicher, dass alle Container mit dem `bigdatanet`-Netzwerk verbunden sind.

### # Die Website
Nun sind die Karten unter [http://<external-ip-of-vm>:5000/](http://<external-ip-of-vm>:5000/) für die Suche verfügbar.

![image](https://github.com/user-attachments/assets/0e3892b8-da1e-4932-9120-8f3461bdb8d3)

Die Bilder sind anklickbar:

![image](https://github.com/user-attachments/assets/19f36be5-0723-4c04-91d5-18bca935e85a)

### # Batch-Prozess
Dies ist ein Batch-Prozess, der alle MTG-Kartendaten auf einmal lädt, was einige Zeit in Anspruch nehmen kann.

![image](https://github.com/user-attachments/assets/2dff15ba-c841-4ef7-829d-c20ac34518f0)

# ETL-Workflow

### # ETL-Workflow
Das folgende Diagramm zeigt den ETL-Workflow des Exam-Projekts. Der Workflow basiert auf der Medallion-Architektur und bereitet die Daten schrittweise durch die Bronze/Silver/Gold-Schichten vor. Im Kontext des Projekts wurde eine zusätzliche Raw-Schicht eingeführt, in der die Daten zunächst als JSON im HDFS gespeichert werden, wie es im Exam-Projekt gefordert ist. Die Gold-Schicht ist als PostgreSQL-Datenbank implementiert und enthält nur die Datensätze, die am Ende des Exam-Projekts benötigt werden: card_id, name, text, artist, image_url. Die Daten sind dann für den Zugriff über eine mit Node.js gehostete Website verfügbar.

![image](https://github.com/user-attachments/assets/753503cc-eaa6-46c0-85f1-19f9f4992040)

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

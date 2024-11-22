# Big Data Exam: MTG-Datenpipeline

## Introduction
This guide provides detailed steps for setting up a Big Data pipeline environment using Docker. The pipeline consists of several key components: Apache Hadoop, Apache Airflow, PostgreSQL, and a Node.js-based web server, all orchestrated within Docker containers. This setup is designed to handle and process data from the Magic: The Gathering API (https://docs.magicthegathering.io/).

## Task description
The task is to make use of this data to build a searchable database of all MTG trading cards.

Workflow:
- Gather data from api.magicthegathering.io
- Save raw data (JSON files) to HDFS
- Optimize, reduce and clean raw data and save it to final
directory on HDFS
- Export MTG data to end-user database (e.g. MySQL,
MongoDB…)
- Provide a simple HTML Frontend which is able to:
  - read from end-user database
  - process user input (card name, text or artist)
  - display search results
- The whole data workflow must be implemented within an ETL
workflow tool (e.g. Pentaho Data Integration or Airflow) and run automatically

# Setup Instructions for the ETL-Workflow:
This section explains how to set up the workflow.

### # Install Docker:
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER # exit and login again
```

### # Create a docker network
To create a custom Docker network that enables communication between containers, use the following command:
```bash
docker network create --driver bridge bigdatanet
```

### # Pull Docker Images
Download the necessary Docker images for Hadoop, Airflow, PostgreSQL, and the Webserver (Node.js):

1. Hadoop Image:
```bash
docker pull marcelmittelstaedt/spark_base:latest
```

2. Airflow Image:
```bash
docker pull marcelmittelstaedt/airflow:latest
```

3. PostgreSQL Image:
4. Version: psql (PostgreSQL) 17.1 (Debian 17.1-1.pgdg120+1)
```bash
docker pull postgres
```

4. Webserver (Node.js):
Version: v22.11.0
```bash
docker pull node
```

### # Run Docker Containers
Start the Docker containers for Hadoop, Airflow, PostgreSQL, and the Webserver. Each component will run in its own container.

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

3. Postgres:
```bash
docker run --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -d --network bigdatanet postgres
```
The Postgres Docker  is now set up to communicate over the Docker network "bigdatanet" and uses the password "admin" for authentication.

4. Webserver (Node.js): Running is recommended later

### # Get Files
Clone the repository and copy the necessary scripts to the respective Docker containers.

1. Clone the Repository:
```bash
git clone https://github.com/grxver7/Big-Data-Exam.git
```

2. Create directory for the website:
```bash
mkdir website_mtg
```

3. Copy Files to the correct environment:

- Copy Python Scripts to Airflow Container:
```bash
for file in /home/lxcx_holder/Big-Data-Exam/python_scripts/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/python/; done
```

- Copy DAGs to Airflow Container:
```bash
for file in /home/lxcx_holder/Big-Data-Exam/DAG/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/dags/; done
```

- Copy Website Files to Webserver:
```bash
for file in /home/lxcx_holder/Big-Data-Exam/website_mtg/*; do
    cp "$file" /home/lxcx_holder/website_mtg/; done
```

### # Modify and Start Services

1. **Hadoop:**
   Log into the Hadoop container and start the Hadoop services:
```bash
docker exec -it hadoop bash
sudo su hadoop
cd
start-all.sh
hiveserver2
```

2. **Airflow:**
   Log into the Airflow container, install necessary Python dependencies, and access the Airflow UI:
```bash
sudo docker exec -it airflow bash
sudo su airflow
pip install mtgsdk
```
   Access Airflow at: [http://<external-ip-of-vm>:8080/admin/](http://<external-ip-of-vm>:8080/admin/)

### # Set Up the Webserver
Use the Dockerfile in the website_mtg directory to build the Node.js-based webserver.

1. Build the Docker image:
```bash
sudo docker build -t mtg-node-app .
```

2. Run the webserver container:
```bash
docker run -it -p 5000:5000 --net bigdatanet --name mtg-node-app mtg-node-app
```
The webserver Docker container is now accessible on port 5000 and can communicate over the "bigdatanet" Docker network.

### # Troubleshooting
- **Airflow is not accessible?** Try restarting the VM or your local machine.
- **Containers not communicating?** Ensure all containers are connected to the `bigdatanet` network.

### # Impressions of the implemented Website
Now the cards are available for search under http://<external-ip-of-vm>:5000/

![image](https://github.com/user-attachments/assets/0e3892b8-da1e-4932-9120-8f3461bdb8d3)

The images are clickable:

![image](https://github.com/user-attachments/assets/19f36be5-0723-4c04-91d5-18bca935e85a)

# Additional Information about the Workflow

### # ETL-Workflow
The following diagram shows the ETL workflow of the exam project. The workflow is based on the concept of the Medallion Architecture, with a stepwise preparation of data through the Bronze/Silver/Gold layers. 
This simplifies, among other things, the implementation of the ETL workflow (by breaking the ETL process into stages, making it also easier to debug and maintain), increases the data quality (each layer improves the data with different task and goals) and enhances the traceability of the data (corrupted data in higher layers can be compared with the data of lower layers).
In the context of the project, an additional Raw layer was introduced, where the data is first stored as JSON in the HDFS, as required in the exam project. The Gold layer is implemented in the form of a PostgreSQL database and contains only the datasets required at the end of the exam project: card_id, name, text, artist, image_url. The data is then made available for consumption on a website hosted with Node.js (on a Docker container).

![image](https://github.com/user-attachments/assets/753503cc-eaa6-46c0-85f1-19f9f4992040)

### # Batch Process
The ETL workflow operates as a batch process, loading and transforming the entire MTG card dataset in a single run. This ensures high-quality data processing but may require significant time to complete. On the Google VM ("c3d-standard-4"), the entire workflow can take up to 20 minutes. The diagram below outlines the estimated duration of each step within the DAG.

![image](https://github.com/user-attachments/assets/9fa5b381-e779-485b-9693-c4dded4951e2)

### # DAG
The workflow is automated using Airflow, with the following steps in the DAG:

![image](https://github.com/user-attachments/assets/87203bda-a907-4ee9-9f10-6422efcfe56b)

1. Create directories (create_hdfs_raw_dir_task, create_hdfs_bronze_dir_task, create_hdfs_silver_dir_task) must happen first to ensure that the HDFS directories exist for storing the data.
2. Cleaning and Uploading Data: Once the directories are created, the system cleans old raw data (delete_old_data_task), uploads new data to HDFS (upload_to_hdfs_task), and then processes it (collect_job_mtg).
3. Data Processing in Layers: The data flows from the raw layer (via collect_job_mtg) to the bronze layer (bronze_job_mtg), then the silver layer (silver_job_mtg), and finally into a PostgreSQL database (ingestDB_job_mtg).

### # Job Description
The table describes each job in the DAG

| Job Name                  | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| create_hdfs_bronze_directory | Creates the directory for the Bronze layer in HDFS.                       |
| create_hdfs_silver_directory | Creates the directory for the Silver layer in HDFS.                       |
| create_raw_directory       | Creates a local directory for temporary storage of raw data.                  |
| create_hdfs_raw_directory  | Creates the HDFS directory for temporary storage of raw data.                               |
| clear_local_raw_dir        | Clears the local directory for raw data to prepare for new data ingestion.           |
| upload_to_hdfs             | Simulates uploading data to HDFS (DummyOperator).                                        |
| collect_job_mtg            | Collects Magic: The Gathering data from the API, saves it as a JSON file locally, and uploads it to HDFS.       |
| bronze_job_mtg             | Converts raw JSON data into Parquet format for the Bronze layer in HDFS.    |
| silver_job_mtg             | Transforms Bronze layer data into a 3NF structure, reducing redundancies and anomalies.   |
| ingestDB_job_mtg           | 	Loads the transformed Silver layer data into the database, including only the necessary fields for reporting.  |

# # The Data
A more detailed description of the data can be found in the supplementary PDF titled "Doku_Datenstruktur_&_Datensammlung.pdf."

### # Example Data from the Silver Layer (3NF)

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

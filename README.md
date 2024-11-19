# Big Data Docker Setup for MTG Data Pipeline

## 1. Introduction
This guide provides detailed steps for setting up a Big Data pipeline environment using Docker. The pipeline involves several components: Apache Hadoop, Apache Airflow, PostgreSQL, and a Node.js-based Webserver, all orchestrated within Docker containers. This setup is designed to handle a Magic: The Gathering (MTG) data pipeline.

## 2. The following shows how to set up the data pipeling for MTG-Data:

### # Install Docker:
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER # exit and login again
```

### # Create a docker network
Create a custom network for the containers:
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
```bash
docker pull postgres
```

4. Webserver (Node.js):
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

3. PostgreSQL:
```bash
docker run --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -d --network bigdatanet postgres
```

4. Webserver (Node.js): Recommended later

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
sudo docker build --no-cache -t mtg-node-app .
```
   or
```bash
sudo docker build -t mtg-node-app .
```

2. Run the webserver container:
```bash
docker run -it -p 5000:5000 --net bigdatanet --name mtg-node-app mtg-node-app
```

### # Troubleshooting
- **Airflow is not accessible?** Try restarting the VM or your local machine.
- **Containers not communicating?** Ensure all containers are connected to the `bigdatanet` network.

### # DAG
The workflow is automated using Airflow, with the following steps in the DAG:

![image](https://github.com/user-attachments/assets/87203bda-a907-4ee9-9f10-6422efcfe56b)

1. Create directories (create_hdfs_raw_dir_task, create_hdfs_bronze_dir_task, create_hdfs_silver_dir_task) must happen first to ensure that the HDFS directories exist for storing the data.
2. Cleaning and Uploading Data: Once the directories are created, the system cleans old raw data (delete_old_data_task), uploads new data to HDFS (upload_to_hdfs_task), and then processes it (collect_job_mtg).
3. Data Processing in Layers: The data flows from the raw layer (via collect_job_mtg) to the bronze layer (bronze_job_mtg), then the silver layer (silver_job_mtg), and finally into a PostgreSQL database (ingestDB_job_mtg).

### # Batch Process
This is a batch process designed to load all MTG card data at once, which may take some time to complete.
![image](https://github.com/user-attachments/assets/2dff15ba-c841-4ef7-829d-c20ac34518f0)

### # The Wbsite
Now the cards are available for search under http://<external-ip-of-vm>:5000/

![image](https://github.com/user-attachments/assets/0e3892b8-da1e-4932-9120-8f3461bdb8d3)

The image are clickable:

![image](https://github.com/user-attachments/assets/19f36be5-0723-4c04-91d5-18bca935e85a)

### # Conclusion
Congratulations! You've now set up a fully operational Docker-based environment for the MTG data pipeline. With Hadoop, Airflow, PostgreSQL, and a Node.js Webserver running in isolated containers, your pipeline is both scalable and easy to manage. You can now begin processing and managing MTG data effectively in your Big Data ecosystem.

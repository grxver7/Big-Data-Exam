# Big Data Docker Setup for MTG Data Pipeline

1. Introduction
This guide provides detailed steps for setting up a Big Data pipeline environment using Docker. The pipeline involves several components: Apache Hadoop, Apache Airflow, PostgreSQL, and a Node.js-based Webserver, all orchestrated within Docker containers. This setup is designed to handle a Magic: The Gathering (MTG) data pipeline.
2. The following shows how to set up the data pipeling for MTG-Data:

# Install Docker
1. sudo apt-get update
2. sudo apt-get install docker.io
3. sudo usermod -aG docker $USER # exit and login again

# Create a docker network
docker network create --driver bridge bigdatanet

# Pull Docker Images
Download the necessary Docker images for Hadoop, Airflow, PostgreSQL, and the Webserver (Node.js):

1. Hadoop Image:
docker pull marcelmittelstaedt/spark_base:latest

2. Airflow Image:
docker pull marcelmittelstaedt/airflow:latest

3. PostgreSQL Image:
docker pull postgres

4. Webserver (Node.js):
docker pull node

# Run Docker Containers
Start the Docker containers for Hadoop, Airflow, PostgreSQL, and the Webserver. Each component will run in its own container.

1. Hadoop:
docker run -dit --name hadoop \
  -p 8088:8088 -p 9870:9870 -p 9864:9864 -p 10000:10000 \
  -p 8032:8032 -p 8030:8030 -p 8031:8031 -p 9000:9000 -p 8888:8888 \
  --net bigdatanet marcelmittelstaedt/spark_base:latest
   
3. Airflow:
docker run -dit --name airflow \
  -p 8080:8080 \
  --net bigdatanet marcelmittelstaedt/airflow:latest
   
5. PostgreSQL:
docker run --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -d --network bigdatanet postgres
6. Webserver (Node.js): recommended later

# Get Files
Clone the repository and copy the necessary scripts to the respective Docker containers.

1. Clone the Repository: git clone https://github.com/grxver7/Big-Data-Exam.git
2. Create directory for website: mkdir website_mtg

3. Copy Files in the correct environment
3.1. Copy Python Scripts to Airflow Container:
for file in /home/lxcx_holder/Big-Data-Exam/python_scripts/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/python/; done

3.2. Copy DAGs to Airflow Container:
for file in /home/lxcx_holder/Big-Data-Exam/DAG/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/dags/; done

3.3. Copy Website Files to Webserver:
for file in /home/lxcx_holder/Big-Data-Exam/website_mtg/*; do
    cp "$file" /home/lxcx_holder/website_mtg/; done

# Modify and Start Services

1. Hadoop:
Log into the Hadoop container and start the Hadoop services:
  docker exec -it hadoop bash
  sudo su hadoop
  cd
  start-all.sh
  hiveserver2
2. Airflow:
Log into the Airflow container, install necessary Python dependencies, and access the Airflow UI:
  sudo docker exec -it airflow bash
  sudo su airflow
  pip install mtgsdk
Access Airflow at: http://<external-ip-of-vm>:8080/admin/

# Set Up the Webserver
Use the Dockerfile
In the website_mtg directory, use the Dockerfile to build the Node.js-based webserver.

# Build the Docker image
sudo docker build --no-cache -t mtg-node-app .
or
sudo docker build -t mtg-node-app .

# Run the webserver container
docker run -it -p 5000:5000 --net bigdatanet --name mtg-node-app mtg-node-app

# Troubleshooting
Airflow is not accessible? Try restarting the VM or your local machine.
Containers not communicating? Ensure all containers are connected to the bigdatanet network.

# Conclusion
Congratulations! You've now set up a fully operational Docker-based environment for the MTG data pipeline. With Hadoop, Airflow, PostgreSQL, and a Node.js Webserver running in isolated containers, your pipeline is both scalable and easy to manage. You can now begin processing and managing MTG data effectively in your Big Data ecosystem.

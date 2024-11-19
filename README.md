Here is the entire guide written as one continuous markdown with code blocks that are easily copyable on GitHub:

markdown
Copy code
# Big Data Docker Setup for MTG Data Pipeline

## 1. Introduction
This guide provides detailed steps for setting up a Big Data pipeline environment using Docker. The pipeline involves several components: Apache Hadoop, Apache Airflow, PostgreSQL, and a Node.js-based Webserver, all orchestrated within Docker containers. This setup is designed to handle a Magic: The Gathering (MTG) data pipeline.

## 2. The following shows how to set up the data pipeline for MTG-Data:

### Install Docker
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER  # exit and login again
Create a Docker network
bash
Copy code
docker network create --driver bridge bigdatanet
Pull Docker Images
Download the necessary Docker images for Hadoop, Airflow, PostgreSQL, and the Webserver (Node.js):

Hadoop Image:
bash
Copy code
docker pull marcelmittelstaedt/spark_base:latest
Airflow Image:
bash
Copy code
docker pull marcelmittelstaedt/airflow:latest
PostgreSQL Image:
bash
Copy code
docker pull postgres
Webserver (Node.js):
bash
Copy code
docker pull node
Run Docker Containers
Start the Docker containers for Hadoop, Airflow, PostgreSQL, and the Webserver. Each component will run in its own container.

Hadoop:
bash
Copy code
docker run -dit --name hadoop \
  -p 8088:8088 -p 9870:9870 -p 9864:9864 -p 10000:10000 \
  -p 8032:8032 -p 8030:8030 -p 8031:8031 -p 9000:9000 -p 8888:8888 \
  --net bigdatanet marcelmittelstaedt/spark_base:latest
Airflow:
bash
Copy code
docker run -dit --name airflow \
  -p 8080:8080 \
  --net bigdatanet marcelmittelstaedt/airflow:latest
PostgreSQL:
bash
Copy code
docker run --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -d --network bigdatanet postgres
Webserver (Node.js): (recommended to build later)
Get Files
Clone the repository and copy the necessary scripts to the respective Docker containers.

Clone the Repository:
bash
Copy code
git clone https://github.com/grxver7/Big-Data-Exam.git
Create a directory for website:
bash
Copy code
mkdir website_mtg
Copy Files into the correct environment:
Copy Python Scripts to the Airflow Container:
bash
Copy code
for file in /home/lxcx_holder/Big-Data-Exam/python_scripts/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/python/; done
Copy DAGs to the Airflow Container:
bash
Copy code
for file in /home/lxcx_holder/Big-Data-Exam/DAG/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/dags/; done
Copy Website Files to the Webserver:
bash
Copy code
for file in /home/lxcx_holder/Big-Data-Exam/website_mtg/*; do
    cp "$file" /home/lxcx_holder/website_mtg/; done
Modify and Start Services
Start Hadoop:
bash
Copy code
docker exec -it hadoop bash
sudo su hadoop
cd
start-all.sh
hiveserver2
Start Airflow:
bash
Copy code
docker exec -it airflow bash
sudo su airflow
pip install mtgsdk
Access Airflow UI at: http://<external-ip-of-vm>:8080/admin/

Set Up the Webserver (Node.js)
Use the Dockerfile in the website_mtg directory to build the Node.js-based webserver.

Build the Docker image:
bash
Copy code
sudo docker build --no-cache -t mtg-node-app .
or

bash
Copy code
sudo docker build -t mtg-node-app .
Run the Webserver Container:
bash
Copy code
docker run -it -p 5000:5000 --net bigdatanet --name mtg-node-app mtg-node-app
Troubleshooting
Airflow is not accessible? Try restarting the VM or your local machine.
Containers not communicating? Ensure all containers are connected to the bigdatanet network.
Conclusion
Congratulations! You've now set up a fully operational Docker-based environment for the MTG data pipeline. With Hadoop, Airflow, PostgreSQL, and a Node.js Webserver running in isolated containers, your pipeline is both scalable and easy to manage. You can now begin processing and managing MTG data effectively in your Big Data ecosystem.

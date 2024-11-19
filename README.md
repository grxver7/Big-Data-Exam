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

bash
Copy code
# Hadoop Image
docker pull marcelmittelstaedt/spark_base:latest

# Airflow Image
docker pull marcelmittelstaedt/airflow:latest

# PostgreSQL Image
docker pull postgres

# Webserver (Node.js)
docker pull node
3.4 Run Docker Containers
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
Webserver (Node.js):
bash
Copy code
docker run -it -p 5000:5000 \
  --net bigdatanet --name mtg-node-app mtg-node-app
3.5 Get Files
Clone the repository and copy the necessary scripts to the respective Docker containers.

Clone the Repository:
bash
Copy code
git clone https://github.com/grxver7/Big-Data-Exam.git
mkdir website_mtg
Copy Python Scripts to Airflow Container:
bash
Copy code
for file in /home/lxcx_holder/Big-Data-Exam/python_scripts/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/python/; done
Copy DAGs to Airflow Container:
bash
Copy code
for file in /home/lxcx_holder/Big-Data-Exam/DAG/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/dags/; done
Copy Website Files to Webserver:
bash
Copy code
for file in /home/lxcx_holder/Big-Data-Exam/website_mtg/*; do
    cp "$file" /home/lxcx_holder/website_mtg/; done
3.6 Modify and Start Services
Hadoop:
Log into the Hadoop container and start the Hadoop services:

bash
Copy code
docker exec -it hadoop bash
sudo su hadoop
cd
start-all.sh
hiveserver2
Airflow:
Log into the Airflow container, install necessary Python dependencies, and access the Airflow UI:

bash
Copy code
sudo docker exec -it airflow bash
sudo su airflow
pip install mtgsdk
Access Airflow at:

arduino
Copy code
http://<external-ip-of-vm>:8080/admin/
3.7 Set Up the Webserver
Modify the Dockerfile
In the website_mtg directory, modify the Dockerfile to build the Node.js-based webserver.

Dockerfile Example:

Dockerfile
Copy code
# Use Node.js as the base image
FROM node:22

# Set the working directory
WORKDIR /usr/src/app

# Install dependencies
RUN echo '{ "name": "my-app", "version": "1.0.0", "dependencies": { "express": "^4.18.2", "pg": "^8.11.0" } }' > package.json
RUN npm install

# Copy the rest of the app files
COPY . .

# Expose the application port
EXPOSE 5000

# Run the server
CMD ["node", "server.js"]
Build and Run the Webserver:
bash
Copy code
# Build the Docker image
sudo docker build --no-cache -t mtg-node-app .

# Run the webserver container
docker run -it -p 5000:5000 --net bigdatanet --name mtg-node-app mtg-node-app
4. Troubleshooting
Airflow is not accessible? Try restarting the VM or your local machine.
Containers not communicating? Ensure all containers are connected to the bigdatanet network.
5. Conclusion
Congratulations! You've now set up a fully operational Docker-based environment for the MTG data pipeline. With Hadoop, Airflow, PostgreSQL, and a Node.js Webserver running in isolated containers, your pipeline is both scalable and easy to manage. You can now begin processing and managing MTG data effectively in your Big Data ecosystem.

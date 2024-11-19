Big Data Docker Setup for MTG Data Pipeline
1. Introduction
This guide sets up the environment for running various Docker containers to manage a Big Data pipeline involving Apache Hadoop, Apache Airflow, PostgreSQL, and a Webserver for a Magic: The Gathering (MTG) data pipeline.

2. Prerequisites
Ensure you have the following installed on your system:

Docker (version 20.10 or higher)
Docker Compose (optional but recommended for orchestration)
3. Installation Steps
3.1 Install Docker
To install Docker, run the following commands:

bash
Copy code
# Update package list
sudo apt-get update

# Install Docker
sudo apt-get install docker.io

# Add your user to the Docker group
sudo usermod -aG docker $USER

# Log out and log back in for the group changes to take effect
3.2 Create Docker Network
Create a dedicated Docker network for all the containers:

bash
Copy code
docker network create --driver bridge bigdatanet
3.3 Pull Docker Images
Download the necessary Docker images for Hadoop, Airflow, PostgreSQL, and the Webserver:

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
Start the Docker containers for Hadoop, Airflow, PostgreSQL, and the Webserver.

Hadoop
bash
Copy code
docker run -dit --name hadoop \
  -p 8088:8088 -p 9870:9870 -p 9864:9864 -p 10000:10000 \
  -p 8032:8032 -p 8030:8030 -p 8031:8031 -p 9000:9000 -p 8888:8888 \
  --net bigdatanet marcelmittelstaedt/spark_base:latest
Airflow
bash
Copy code
docker run -dit --name airflow \
  -p 8080:8080 \
  --net bigdatanet marcelmittelstaedt/airflow:latest
PostgreSQL
bash
Copy code
sudo docker run --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -d --network bigdatanet postgres
Webserver (Node.js)
bash
Copy code
docker run -it -p 5000:5000 \
  --net bigdatanet --name mtg-node-app mtg-node-app
3.5 Get Files
Clone the repository and distribute the scripts to the appropriate directories inside Docker containers.

Clone Repository
bash
Copy code
git clone https://github.com/grxver7/Big-Data-Exam.git
mkdir website_mtg
Copy Python Scripts to Airflow Container
bash
Copy code
for file in /home/lxcx_holder/Big-Data-Exam/python_scripts/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/python/; done
Copy DAGs to Airflow Container
bash
Copy code
for file in /home/lxcx_holder/Big-Data-Exam/DAG/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/dags/; done
Copy Website Files to Webserver
bash
Copy code
for file in /home/lxcx_holder/Big-Data-Exam/website_mtg/*; do
    cp "$file" /home/lxcx_holder/website_mtg/; done
3.6 Modify and Start Services
Hadoop
Log into the Hadoop container and start the Hadoop services:

bash
Copy code
docker exec -it hadoop bash
sudo su hadoop
cd
start-all.sh
hiveserver2
Airflow
Log into the Airflow container and install necessary Python dependencies:

bash
Copy code
sudo docker exec -it airflow bash
sudo su airflow
pip install mtgsdk
Then, access Airflow at:

arduino
Copy code
http://<external-ip-of-vm>:8080/admin/
3.7 Set Up the Webserver
Modify the Dockerfile in the website_mtg directory to build the Node.js webserver.

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
Build and Run the Webserver
bash
Copy code
# Build the Docker image
sudo docker build --no-cache -t mtg-node-app .

# Run the webserver container
docker run -it -p 5000:5000 --net bigdatanet --name mtg-node-app mtg-node-app
4. Troubleshooting
If Airflow is not accessible, try restarting the VM or the local machine.
Ensure that all containers are connected to the bigdatanet network.
5. Conclusion
You now have a fully set up Docker-based environment with Hadoop, Airflow, PostgreSQL, and a Node.js Webserver for the MTG data pipeline. The services are running in isolated containers, ensuring a scalable and manageable setup.

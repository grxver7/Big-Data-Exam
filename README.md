# Install Docker
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER  # exit and login again

# Create a docker network
docker network create --driver bridge bigdatanet

# Pull Docker Images
# Hadoop Image
docker pull marcelmittelstaedt/spark_base:latest

# Airflow Image
docker pull marcelmittelstaedt/airflow:latest

# PostgreSQL Image
docker pull postgres

# Webserver (Node.js)
docker pull node

# Run Docker Containers
# Hadoop
docker run -dit --name hadoop \
  -p 8088:8088 -p 9870:9870 -p 9864:9864 -p 10000:10000 \
  -p 8032:8032 -p 8030:8030 -p 8031:8031 -p 9000:9000 -p 8888:8888 \
  --net bigdatanet marcelmittelstaedt/spark_base:latest

# Airflow
docker run -dit --name airflow \
  -p 8080:8080 \
  --net bigdatanet marcelmittelstaedt/airflow:latest

# PostgreSQL
docker run --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -d --network bigdatanet postgres

# Webserver (Node.js) – recommended to build later
# Get Files
# Clone the Repository
git clone https://github.com/grxver7/Big-Data-Exam.git

# Create directory for website
mkdir website_mtg

# Copy Files to Docker Containers
# Copy Python Scripts to Airflow Container
for file in /home/lxcx_holder/Big-Data-Exam/python_scripts/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/python/; done

# Copy DAGs to Airflow Container
for file in /home/lxcx_holder/Big-Data-Exam/DAG/*; do
    sudo docker cp "$file" airflow:/home/airflow/airflow/dags/; done

# Copy Website Files to Webserver
for file in /home/lxcx_holder/Big-Data-Exam/website_mtg/*; do
    cp "$file" /home/lxcx_holder/website_mtg/; done

# Modify and Start Services

# Start Hadoop
docker exec -it hadoop bash
sudo su hadoop
cd
start-all.sh
hiveserver2

# Start Airflow
docker exec -it airflow bash
sudo su airflow
pip install mtgsdk
# Access Airflow UI at: http://<external-ip-of-vm>:8080/admin/

# Set Up the Webserver (Node.js)
# Use Dockerfile to build the Node.js-based webserver
cd website_mtg
sudo docker build --no-cache -t mtg-node-app .

# Run the Webserver Container
docker run -it -p 5000:5000 --net bigdatanet --name mtg-node-app mtg-node-app

# Troubleshooting
# Airflow is not accessible? Try restarting the VM or your local machine.
# Containers not communicating? Ensure all containers are connected to the bigdatanet network.

# Conclusion
# Now, you've set up the Big Data pipeline with Hadoop, Airflow, PostgreSQL, and Node.js in Docker containers. You can now begin processing and managing MTG data effectively in your ecosystem.

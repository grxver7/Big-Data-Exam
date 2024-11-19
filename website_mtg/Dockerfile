# Use Node.js as the base image
FROM node:22

# Set the working directory to the directory where the Dockerfile is located
WORKDIR /usr/src/app

# Create package.json with necessary dependencies
RUN echo '{ "name": "my-app", "version": "1.0.0", "dependencies": { "express": "^4.18.2", "pg": "^8.11.0" } }' >

# Install dependencies (express and pg)
RUN npm install

# Copy the rest of the app files
COPY . .

# Expose the application port
EXPOSE 5000

# Run the server
CMD ["node", "server.js"]
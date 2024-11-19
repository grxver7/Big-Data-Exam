const express = require('express');
const path = require('path');
const { Client } = require('pg');

const app = express();
const port = 5000;

// PostgreSQL Connection
const client = new Client({
    host: 'postgres',  // Ensure 'postgres' matches your PostgreSQL container name or service
    port: 5432,
    user: 'postgres',
    password: 'admin',
    database: 'postgres'  // Make sure 'mtg_db' is your actual database name
});

client.connect();

// Serve the static `index.html` file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Search endpoint
app.get('/search', async (req, res) => {
    const searchQuery = req.query.query;
    const queryText = `
        SELECT card_id, name, image_url
        FROM mtg_db
        WHERE name ILIKE $1 OR text ILIKE $1 OR artist ILIKE $1
    `;

    try {
        const result = await client.query(queryText, [`%${searchQuery}%`]);

        // If no cards are found, return 404
        if (result.rows.length === 0) {
            return res.status(404).send("No cards found.");
        }

        res.json(result.rows);
    } catch (err) {
        console.error("Error querying the database", err);
        res.status(500).send("Error retrieving data");
    }
});

// Start the server
app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://localhost:${port}`);
});

import express from 'express';
import fetch from 'node-fetch';
import bodyParser from 'body-parser';

const app = express();
const port = 3000;

app.use(bodyParser.json());

// Endpoint to handle forwarding the video link
app.post('/send-video-link', async (req, res) => {
    const { videoId } = req.body;

    if (!videoId) {
        return res.status(400).json({ success: false, error: 'Missing videoId' });
    }

    try {
        console.log(`Received video link for video ID: ${videoId}`);
        
        const botServerUrl = 'https://your-bot-server.com/send-video-link';
        const response = await fetch(botServerUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ videoId })
        });

        const data = await response.json();
        console.log('Response from bot server:', data);
        
        res.json({ success: true, message: 'Video link sent!' });
    } catch (error) {
        console.error('Error sending video link:', error);
        res.status(500).json({ success: false, error: 'Internal Server Error' });
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});

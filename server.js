import express from 'express';
import fetch from 'node-fetch';
import bodyParser from 'body-parser';

const app = express();
const port = 3000;

app.use(bodyParser.json());

// Endpoint to handle forwarding the video link
app.post('/send-video-link', async (req, res) => {
    const { videoId } = req.body;

    console.log('Received request with video ID:', videoId); // Log request for debugging

    if (!videoId) {
        return res.status(400).json({ success: false, error: 'Missing videoId' });
    }

    try {
        console.log(`Received video link for video ID: ${videoId}`);

        // Retrieve video link from your database or another source
        const videoLink = await getVideoLinkFromDatabase(videoId);

        if (!videoLink) {
            console.log('Video not found in database'); // Log if video not found
            return res.status(404).json({ success: false, error: 'Video not found' });
        }

        // Send the video link to the bot
        const botServerUrl = 'https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage';
        const response = await fetch(botServerUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: '<USER_CHAT_ID>',
                text: `Here is your video link: ${videoLink}`
            })
        });

        const data = await response.json();
        console.log('Response from bot server:', data); // Log response from bot server
        
        res.json({ success: true, message: 'Video link sent!' });
    } catch (error) {
        console.error('Error sending video link:', error); // Log error for debugging
        res.status(500).json({ success: false, error: 'Internal Server Error' });
    }
});

// Function to retrieve video link from your database
async function getVideoLinkFromDatabase(videoId) {
    // Implement your logic to retrieve the video link using the videoId
    // For example, query your database and return the link
    console.log(`Retrieving video link for ID: ${videoId}`); // Log retrieval process
    return `https://your-video-storage.com/videos/${videoId}.mp4`;
}

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});

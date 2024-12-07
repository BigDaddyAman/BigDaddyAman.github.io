const fetch = require('node-fetch');

exports.handler = async function(event, context) {
    console.log("Function invoked"); // Log when function is invoked

    if (event.httpMethod !== 'POST') {
        console.log("Invalid method:", event.httpMethod); // Log invalid method
        return {
            statusCode: 405,
            body: JSON.stringify({ success: false, error: 'Method Not Allowed' })
        };
    }

    let body;
    try {
        body = JSON.parse(event.body);
        console.log("Parsed body:", body); // Log parsed body
    } catch (err) {
        console.log("Error parsing body:", err); // Log body parsing error
        return {
            statusCode: 400,
            body: JSON.stringify({ success: false, error: 'Invalid JSON' })
        };
    }

    const { videoId } = body;

    if (!videoId) {
        console.log("Missing videoId"); // Log missing videoId
        return {
            statusCode: 400,
            body: JSON.stringify({ success: false, error: 'Missing videoId' })
        };
    }

    try {
        console.log(`Received video link for video ID: ${videoId}`);

        // Retrieve video link from your database or another source
        const videoLink = await getVideoLinkFromDatabase(videoId);

        if (!videoLink) {
            console.log('Video not found in database'); // Log if video not found
            return {
                statusCode: 404,
                body: JSON.stringify({ success: false, error: 'Video not found' })
            };
        }

        // Send the video link to the bot
        const botServerUrl = `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage`;
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

        return {
            statusCode: 200,
            body: JSON.stringify({ success: true, message: 'Video link sent!' })
        };
    } catch (error) {
        console.error('Error sending video link:', error); // Log error for debugging
        return {
            statusCode: 500,
            body: JSON.stringify({ success: false, error: 'Internal Server Error' })
        };
    }
};

// Function to retrieve video link from your database
async function getVideoLinkFromDatabase(videoId) {
    console.log(`Retrieving video link for ID: ${videoId}`); // Log retrieval process
    // Simulating retrieval process; replace with actual database logic
    return `https://your-video-storage.com/videos/${videoId}.mp4`;
}

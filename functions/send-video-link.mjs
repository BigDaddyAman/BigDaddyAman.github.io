const fetch = require('node-fetch');

exports.handler = async function(event, context) {
    console.log("Function invoked");

    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            body: JSON.stringify({ success: true })
        };
    }

    if (event.httpMethod !== 'POST') {
        console.log("Invalid method:", event.httpMethod);
        return {
            statusCode: 405,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            body: JSON.stringify({ success: false, error: 'Method Not Allowed' })
        };
    }

    let body;
    try {
        body = JSON.parse(event.body);
        console.log("Parsed body:", body);
    } catch (err) {
        console.log("Error parsing body:", err);
        return {
            statusCode: 400,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            body: JSON.stringify({ success: false, error: 'Invalid JSON' })
        };
    }

    const { videoId } = body;

    if (!videoId) {
        console.log("Missing videoId");
        return {
            statusCode: 400,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            body: JSON.stringify({ success: false, error: 'Missing videoId' })
        };
    }

    try {
        console.log(`Received video link for video ID: ${videoId}`);

        const videoLink = await getVideoLinkFromDatabase(videoId);

        if (!videoLink) {
            console.log('Video not found in database');
            return {
                statusCode: 404,
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                body: JSON.stringify({ success: false, error: 'Video not found' })
            };
        }

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
        console.log('Response from bot server:', data);

        return {
            statusCode: 200,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            body: JSON.stringify({ success: true, message: 'Video link sent!' })
        };
    } catch (error) {
        console.error('Error sending video link:', error);
        return {
            statusCode: 500,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            body: JSON.stringify({ success: false, error: 'Internal Server Error' })
        };
    }
};

async function getVideoLinkFromDatabase(videoId) {
    console.log(`Retrieving video link for ID: ${videoId}`);
    return `https://your-video-storage.com/videos/${videoId}.mp4`;
}

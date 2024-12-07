const fetch = require('node-fetch');

exports.handler = async function(event, context) {
    console.log("Function invoked");

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

        // Retrieve video link from your database or another source
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

        // Send the video link to the bot
        const bot
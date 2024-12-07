const axios = require("axios");

exports.handler = async function (event, context) {
  const queryParams = event.queryStringParameters;
  const token = queryParams.token;

  if (!token) {
    return {
      statusCode: 400,
      body: JSON.stringify({ message: "Token is missing!" }),
    };
  }

  // Simulate token validation (You should verify this with your database)
  const isValidToken = token === "12345"; // Replace this with actual token verification logic

  if (!isValidToken) {
    return {
      statusCode: 403,
      body: JSON.stringify({ message: "Invalid or expired token!" }),
    };
  }

  // Use Telegram Bot API to fetch the file
  try {
    const TELEGRAM_BOT_TOKEN = "7615071981:AAFohL0Rb10_U2fALN1t8ns5vPMI5d6sEA0";
    const CHAT_ID = "YOUR_CHAT_ID"; // Replace with chat ID where the file is stored
    const FILE_ID = "YOUR_FILE_ID"; // Replace with the file ID corresponding to this token

    const fileInfo = await axios.get(
      `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getFile?file_id=${FILE_ID}`
    );

    const filePath = fileInfo.data.result.file_path;
    const fileUrl = `https://api.telegram.org/file/bot${TELEGRAM_BOT_TOKEN}/${filePath}`;

    return {
      statusCode: 200,
      body: JSON.stringify({ download_url: fileUrl }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ message: "Failed to fetch the file!" }),
    };
  }
};

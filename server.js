import express from 'express'; // Use import for express
import fetch from 'node-fetch';
import bodyParser from 'body-parser';

const app = express();
const port = 3000;

app.use(bodyParser.json());

app.post('/verify-captcha', (req, res) => {
    const secretKey = '6LeH9pQqAAAAAE7u53YfzkuM8Kd7hKKZiFs3ycyB';
    const token = req.body['recaptcha_token'];

    const verificationUrl = `https://www.google.com/recaptcha/api/siteverify?secret=${secretKey}&response=${token}`;

    fetch(verificationUrl, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                res.json({ success: true });
            } else {
                res.json({ success: false });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            res.status(500).json({ success: false, error: 'Internal Server Error' });
        });
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});

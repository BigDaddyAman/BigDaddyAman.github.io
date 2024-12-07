document.getElementById('captcha-form').onsubmit = function(event) {
    event.preventDefault();

    const recaptchaResponse = grecaptcha.getResponse();
    if (!recaptchaResponse) {
        alert("Please complete the CAPTCHA");
        return;
    }

    // Send the CAPTCHA response to your server for verification
    fetch('https://your-api-endpoint.com/verify-captcha', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'g-recaptcha-response': recaptchaResponse })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              alert("CAPTCHA verified! Proceed with your next steps.");
          } else {
              alert("CAPTCHA verification failed. Please try again.");
          }
      })
      .catch(error => {
          console.error('Error:', error);
      });
};

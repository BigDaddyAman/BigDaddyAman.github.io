document.getElementById('captcha-form').onsubmit = function(event) {
    event.preventDefault();

    grecaptcha.ready(function() {
        grecaptcha.execute('6LeH9pQqAAAAAPdEyc7IJS0woEx3ujyqOYNM7lwC', {action: 'submit'}).then(function(token) {
            document.getElementById('recaptcha_token').value = token;

            // Now submit the form
            fetch('https://your-api-endpoint.com/verify-captcha', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 'recaptcha_token': token })
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
        });
    });
};

// reCAPTCHA callback function
function onRecaptchaSuccess(token) {
    // Enable submit button
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = false;
    }
}

// Initialize reCAPTCHA
document.addEventListener('DOMContentLoaded', function () {
    // Load reCAPTCHA script
    const script = document.createElement('script');
    script.src = 'https://www.google.com/recaptcha/api.js';
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
}); 
document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap modal
    const authModal = new bootstrap.Modal(document.getElementById('auth-modal'));

    // Show registration modal when clicking register link
    document.querySelectorAll('.show-register-modal').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            fetch('/accounts/register/email/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('auth-modal').innerHTML = html;
                    authModal.show();
                });
        });
    });

    // Handle form submissions
    document.addEventListener('htmx:afterSwap', function (evt) {
        if (evt.detail.target.id === 'auth-modal') {
            // Focus on input field if present
            const input = evt.detail.target.querySelector('input:not([type=hidden])');
            if (input) {
                input.focus();
            }
        }
    });

    // Handle registration success
    document.addEventListener('htmx:afterSettle', function (evt) {
        if (evt.detail.target.id === 'auth-modal' &&
            evt.detail.innerHTML.includes('Registration successful')) {
            // Hide modal and reload page after successful registration
            setTimeout(() => {
                authModal.hide();
                window.location.reload();
            }, 1000);
        }
    });
}); 
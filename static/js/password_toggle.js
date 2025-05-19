// Function for toggling password visibility
function togglePassword(button) {
    console.log('Toggle password clicked');
    const targetId = button.getAttribute('data-target');
    console.log('Target ID:', targetId);
    const input = document.getElementById(targetId);
    console.log('Input element:', input);
    const icon = button.querySelector('i');
    console.log('Icon element:', icon);

    if (input && icon) {
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
}

// Function to initialize password toggle buttons
function initPasswordToggles() {
    console.log('Initializing password toggles');
    const toggleButtons = document.querySelectorAll('.toggle-password');
    console.log('Found toggle buttons:', toggleButtons.length);
    toggleButtons.forEach(button => {
        // Remove existing event listeners
        button.replaceWith(button.cloneNode(true));
    });
    // Add new event listeners
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function () {
            togglePassword(this);
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initPasswordToggles);

// Make functions available globally
window.togglePassword = togglePassword;
window.initPasswordToggles = initPasswordToggles;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        togglePassword,
        initPasswordToggles
    };
} 
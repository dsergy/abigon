// Handle avatar upload
document.querySelector('.save-avatar')?.addEventListener('click', async function () {
    const avatarInput = document.getElementById('avatarInput');
    if (!avatarInput.files || !avatarInput.files[0]) {
        alert('Please select a file first');
        return;
    }

    const formData = new FormData();
    formData.append('avatar', avatarInput.files[0]);

    try {
        const response = await fetch('/accounts/profile/settings/update/avatar/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        });

        const data = await response.json();
        if (data.status === 'success') {
            // Update avatar display
            const avatarContainer = document.querySelector('.setting-value.d-flex');
            avatarContainer.innerHTML = `<img src="${data.avatar_url}" alt="User avatar" class="avatar-image me-3">`;
            // Close edit form
            const cancelBtn = document.querySelector('.save-avatar').closest('.setting-item').querySelector('.cancel-edit');
            cancelBtn.click();
        } else {
            alert(data.message || 'Failed to update avatar');
        }
    } catch (error) {
        console.error('Error updating avatar:', error);
        alert('Error updating avatar');
    }
}); 
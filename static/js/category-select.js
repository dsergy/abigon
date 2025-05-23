document.addEventListener('DOMContentLoaded', function () {
    const mainCategorySelect = document.getElementById('id_main_category');
    const subCategorySelect = document.getElementById('id_sub_category');

    if (mainCategorySelect && subCategorySelect) {
        mainCategorySelect.addEventListener('change', function () {
            const mainCategoryId = this.value;

            // Clear current options
            subCategorySelect.innerHTML = '<option value="">Select subcategory</option>';

            if (mainCategoryId) {
                // Fetch subcategories for selected main category
                fetch(`/ads/api/subcategories/?main_category=${mainCategoryId}`)
                    .then(response => response.json())
                    .then(data => {
                        data.forEach(subcategory => {
                            const option = document.createElement('option');
                            option.value = subcategory.id;
                            option.textContent = subcategory.name;
                            subCategorySelect.appendChild(option);
                        });
                    });
            }
        });
    }
}); 
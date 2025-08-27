// Add module selector functionality

document.addEventListener('DOMContentLoaded', function() {
    // Handle module selection dropdown
    const moduleSelector = document.getElementById('moduleSelector');
    const goButton = document.getElementById('goToModule');
    
    if (moduleSelector && goButton) {
        goButton.addEventListener('click', function() {
            const selectedValue = moduleSelector.value;
            if (selectedValue) {
                window.location.href = selectedValue;
            }
        });
        
        // Also allow selection by pressing Enter
        moduleSelector.addEventListener('change', function() {
            const selectedValue = moduleSelector.value;
            if (selectedValue) {
                window.location.href = selectedValue;
            }
        });
    }
});

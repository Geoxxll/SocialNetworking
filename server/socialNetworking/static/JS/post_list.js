document.addEventListener('DOMContentLoaded', function () {
    var contentTypeSelect = document.getElementById('id_contentType');
    var contentTextInput = document.getElementById('id_text_content');
    var contentFileInput = document.getElementById('id_image_content');

    // Function to toggle field visibility
    function toggleContentInput() {
        var contentType = contentTypeSelect.value;
        if (contentType === 'text/markdown' || contentType === 'text/plain') {
            contentTextInput.style.display = 'block';  // Show text area
            contentFileInput.style.display = 'none';   // Hide file input
        } else {
            contentTextInput.style.display = 'none';   // Hide text area
            contentFileInput.style.display = 'block';  // Show file input
        }
    }

    // Listen for changes to the contentType select box
    contentTypeSelect.addEventListener('change', toggleContentInput);

    // Initialize correct field visibility on page load
    toggleContentInput();
});
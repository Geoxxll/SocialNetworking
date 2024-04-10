document.addEventListener('DOMContentLoaded', function () {
    var contentTypeSelect = document.getElementById('id_contentType');
    var contentInputWrapper = document.getElementById('content-input-wrapper');
    var contentTextArea = document.getElementById('id_text_content');
    // for markedDown preview
    var markedDownPreviewArea = document.getElementById('markdown-preview');
    var markedDownPreviewTitle = document.getElementById('markdown-preview-title');
    // Function to toggle field visibility
    function toggleContentInput() {
        var contentType = contentTypeSelect.value;
        if (contentType === 'text/markdown' || contentType === 'text/plain') {
            contentTextArea.style.display = 'block' //show text area
        } else {
            
            contentTextArea.style.display = 'none' // hide text area
            contentInputWrapper.innerHTML = '<input type="file" id="id_image_content" name="content">';
        }

        
    }

    // Listen for changes to the contentType select box
    contentTypeSelect.addEventListener('change', toggleContentInput);

    // Initialize correct field visibility on page load
    toggleContentInput();
});
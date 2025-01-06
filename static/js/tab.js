// Get all tab elements
const tabs = document.querySelectorAll('.tabs li');
// Get all tab content elements
const tabContents = document.querySelectorAll('.tab-content');

// Initialize the display (show the first tab content by default)
document.getElementById('video-content').style.display = 'block';

// Add click event listener to each tab
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove 'active' class from all tabs
        tabs.forEach(t => t.classList.remove('active'));
        // Hide all tab contents
        tabContents.forEach(content => content.style.display = 'none');

        // Add 'active' class to clicked tab
        tab.classList.add('active');
        // Show the content related to the clicked tab
        const contentId = tab.id.replace('-tab', '-content');
        document.getElementById(contentId).style.display = 'block';
    });
});

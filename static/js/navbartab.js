document.addEventListener('DOMContentLoaded', function() {
    const activeTabId = localStorage.getItem('activeTabId');
    if (activeTabId) {
        const activeTab = document.querySelector(`#${activeTabId}`);
        if (activeTab) {
            const tab = new bootstrap.Tab(activeTab);
            tab.show();
        }
    }

    const tabs = document.querySelectorAll('.nav-tabs button');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('id');
            localStorage.setItem('activeTabId', tabId);
        });
    });
});
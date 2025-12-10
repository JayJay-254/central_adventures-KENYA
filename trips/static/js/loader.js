// Page Loader Handler
document.addEventListener('DOMContentLoaded', function() {
    const loader = document.getElementById('page-loader');
    
    if (loader) {
        // Hide loader after page fully loads (with slight delay for smooth fade)
        setTimeout(function() {
            loader.classList.add('hide');
        }, 300);
    }
});

// Also hide loader when all resources are loaded
window.addEventListener('load', function() {
    const loader = document.getElementById('page-loader');
    if (loader) {
        loader.classList.add('hide');
    }
});

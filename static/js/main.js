/**
 * Main JavaScript file for IT Services Company
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Auto-dismiss alerts
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // File input display filename
    document.querySelectorAll('.custom-file-input').forEach(function(input) {
        input.addEventListener('change', function(e) {
            var fileName = e.target.files[0].name;
            var label = e.target.nextElementSibling;
            label.innerHTML = fileName;
        });
    });
});

/**
 * Certificate preview and verification functionality
 */
const certificateModule = {
    init: function() {
        // Certificate verification form handling
        const verifyForm = document.getElementById('certificate-verify-form');
        if (verifyForm) {
            verifyForm.addEventListener('submit', function(e) {
                // Form will submit normally, handled by backend
            });
        }

        // Initialize certificate QR code scanner if available
        const qrScanner = document.getElementById('qr-scanner');
        if (qrScanner && typeof Html5QrcodeScanner !== 'undefined') {
            certificateModule.initQRScanner();
        }
    },

    initQRScanner: function() {
        // This would initialize a QR code scanner if the library is included
        // For simplicity, we're not implementing the actual scanner here
        console.log('QR scanner would be initialized here');
    }
};

// Initialize certificate functionality if relevant elements exist
if (document.querySelector('[data-certificate]')) {
    certificateModule.init();
}

/**
 * Admin dashboard functionality
 */
const adminModule = {
    init: function() {
        // Handle delete confirmations
        document.querySelectorAll('.delete-confirm').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                return confirm('Are you sure you want to delete this item? This action cannot be undone.');
            });
        });

        // Handle status updates
        document.querySelectorAll('.status-toggle').forEach(function(element) {
            element.addEventListener('change', function(e) {
                const itemId = this.dataset.itemId;
                const itemType = this.dataset.itemType;
                const isActive = this.checked;
                
                // This would typically make an AJAX request to update the status
                console.log(`Status of ${itemType} with ID ${itemId} set to ${isActive}`);
            });
        });
    }
};

// Initialize admin functionality if on admin page
if (document.querySelector('.admin-content')) {
    adminModule.init();
}
/* Main JavaScript for RentTrack */

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function(el) {
        new bootstrap.Tooltip(el);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Confirm deletion
    document.querySelectorAll('form[onsubmit]').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const onsubmit = form.getAttribute('onsubmit');
            if (onsubmit && onsubmit.includes('confirm')) {
                const result = eval(onsubmit);
                if (!result) {
                    e.preventDefault();
                }
            }
        });
    });

    // Date input defaults to today if empty
    document.querySelectorAll('input[type="date"]').forEach(function(input) {
        if (!input.value && input.classList.contains('default-today')) {
            input.valueAsDate = new Date();
        }
    });

    // Amount input validation
    document.querySelectorAll('input[type="number"]').forEach(function(input) {
        if (input.step === '0.01') {
            input.addEventListener('blur', function() {
                if (this.value) {
                    this.value = parseFloat(this.value).toFixed(2);
                }
            });
        }
    });
});

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Calculate days between dates
function daysBetween(date1, date2) {
    const oneDay = 24 * 60 * 60 * 1000;
    return Math.round((date2 - date1) / oneDay);
}

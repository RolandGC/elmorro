/**
 * Print manager for handling both PDF and ZPL formats
 * Detects Android devices and uses appropriate format
 */

function detectAndroid() {
    /**
     * Detect if device is Android
     */
    return /Android/i.test(navigator.userAgent);
}

function printTicket(saleId, useZPL = null) {
    /**
     * Print ticket in appropriate format
     * 
     * @param {number} saleId - Sale ID to print
     * @param {boolean|null} useZPL - Force ZPL format (null = auto-detect Android)
     */
    
    // Auto-detect Android if not specified
    if (useZPL === null) {
        useZPL = detectAndroid();
    }
    
    const format = useZPL ? 'zpl' : 'pdf';
    const url = `/pos/crm/sale/print/voucher/${saleId}/?format=${format}`;
    
    if (useZPL) {
        // For ZPL, open in new window to allow sending to printer
        const win = window.open(url, 'Print', 'left=200, top=200, width=800, height=500, toolbar=0, resizable=1');
        if (win) {
            win.addEventListener('load', function() {
                // Auto-select all and copy for easy transfer to printer app
                const text = win.document.body.innerText;
                console.log('ZPL Content ready for Zebra printer');
            });
        }
    } else {
        // For PDF, open and print
        const printWindow = window.open(url, 'Print', 'left=200, top=200, width=950, height=500, toolbar=0, resizable=0');
        if (printWindow) {
            printWindow.addEventListener('load', function() {
                printWindow.print();
            }, true);
        }
    }
}

function printTicketPDF(saleId) {
    /**
     * Force print as PDF
     */
    printTicket(saleId, false);
}

function printTicketZPL(saleId) {
    /**
     * Force print as ZPL
     */
    printTicket(saleId, true);
}

/**
 * Auto-replace print buttons on Android devices
 */
document.addEventListener('DOMContentLoaded', function() {
    if (detectAndroid()) {
        // Add visual indicator that Android device detected
        const buttons = document.querySelectorAll('a.btn-primary[href*="/pos/crm/sale/print/voucher/"]');
        buttons.forEach(button => {
            // Convert href to use ZPL format
            const href = button.getAttribute('href');
            const saleId = href.match(/\/(\d+)\//)[1];
            
            button.removeAttribute('href');
            button.setAttribute('onclick', `printTicket(${saleId}); return false;`);
            button.style.cursor = 'pointer';
            
            // Add badge indicating ZPL mode
            if (!button.querySelector('.zpl-indicator')) {
                const badge = document.createElement('small');
                badge.className = 'zpl-indicator';
                badge.textContent = ' [ZPL]';
                badge.style.fontSize = '0.75em';
                badge.style.marginLeft = '5px';
                badge.style.opacity = '0.7';
                button.appendChild(badge);
            }
        });
    }
});

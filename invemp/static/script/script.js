document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('form.delete-form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      if (!confirm('Are you sure you want to delete this entry? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });
});

function makeTablesSortable() {
    document.querySelectorAll("table.sortable").forEach(function(table) {
        // Only attach client-side sorting if NOT the main paginated table
        if (table.id === "main-table") return;
        const ths = table.querySelectorAll("thead th");
        ths.forEach((th, colIndex) => {
            th.onclick = null; // Remove previous listeners
            th.addEventListener("click", function() {
                sortTable(table, colIndex);
            });
        });
    });
}

let loaderStartTime = null;
function showLoader() {
  loaderStartTime = Date.now();
  document.getElementById('global-loader').style.display = 'flex';
}
function hideLoader() {
  const minDuration = 1200; // 1.2 seconds
  const elapsed = Date.now() - loaderStartTime;
  if (elapsed < minDuration) {
    setTimeout(() => {
      document.getElementById('global-loader').style.display = 'none';
    }, minDuration - elapsed);
  } else {
    document.getElementById('global-loader').style.display = 'none';
  }
}

// Function to update table content via AJAX
function updateTableContent(url) {
    showLoader();
    return fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTable = doc.querySelector('#main-table');
        const newPagination = doc.querySelector('.pagination');
        const main = document.getElementById('tables-view');

        if (newTable && main) {
            const oldTable = main.querySelector('#main-table');
            if (oldTable) oldTable.replaceWith(newTable);
        }
        if (main && newPagination) {
            const oldPagination = main.querySelector('.pagination');
            if (oldPagination) {
                oldPagination.replaceWith(newPagination);
            } else {
                main.appendChild(newPagination);
            }
        }

        // Re-attach event listeners
        setupAjaxPagination();
        makeTablesSortable();
        updateExportLinks();
    })
    .finally(() => {
        hideLoader();
    });
}

// Update export links to match current URL (page, filters)
function updateExportLinks() {
    const pdfBtn = document.getElementById('btn-pdf');
    const qrBtn = document.getElementById('btn-qr');
    if (!pdfBtn && !qrBtn) return;
    // Get current URL and query params
    const url = new URL(window.location.href);
    const params = url.search;
    // Extract table_name from pathname (e.g., /items)
    const pathParts = url.pathname.split('/').filter(Boolean);
    let tableName = null;
    if (pathParts.length > 0) {
        // If first part is dashboard_user or similar, skip it
        if (pathParts[0] === 'dashboard_user') {
            tableName = pathParts[1] || 'items';
        } else {
            tableName = pathParts[0];
        }
    }
    if (!tableName) tableName = 'items';
    // Build new export URLs
    if (pdfBtn) {
        pdfBtn.href = `/${tableName}/convert_pdf${params}`;
    }
    if (qrBtn) {
        qrBtn.href = `/${tableName}/convert_pdf_qr${params}`;
    }
}

// Setup AJAX pagination
function setupAjaxPagination() {
    const main = document.getElementById('tables-view');
    if (!main) return;

    main.querySelectorAll('.pagination a').forEach(function(link) {
        if (link.classList.contains('active') || link.getAttribute('href') === '#') return;
        
        link.addEventListener('click', function(e) {
            e.preventDefault();
            updateTableContent(link.href);
            // Update URL without page reload
            history.pushState({}, '', link.href);
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    setupAjaxPagination();
    makeTablesSortable();
    updateExportLinks();
});

// Handle filtering
document.addEventListener('DOMContentLoaded', function() {
    const filterInput = document.getElementById('filter-input');
    const filterForm = document.getElementById('filter-form');
    let debounceTimeout = null;
    let fullReloadTimeout = null;

    if (filterInput && filterForm) {
        filterInput.addEventListener('input', function(e) {
            clearTimeout(debounceTimeout);
            clearTimeout(fullReloadTimeout);
            debounceTimeout = setTimeout(() => {
                const formData = new FormData(filterForm);
                formData.set('page', '1'); // Reset to first page when filtering
                const params = new URLSearchParams(formData).toString();
                const url = filterForm.action + '?' + params;
                updateTableContent(url).then(() => {
                    // Update URL without page reload
                    history.pushState({}, '', url);
                    updateExportLinks();
                    filterInput.focus();
                });
            }, 600);
            // After 2 seconds of no typing, do a full page reload
            fullReloadTimeout = setTimeout(() => {
                window.location.reload();
            }, 2000);
        });

        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
        });
    }
    // Auto-hide flash messages after 2.5 seconds
    setTimeout(function() {
        document.querySelectorAll('.flash').forEach(function(flash) {
            flash.style.transition = 'opacity 0.5s';
            flash.style.opacity = '0';
            setTimeout(function() {
                if (flash.parentNode) {
                    flash.parentNode.removeChild(flash);
                }
            }, 500);
        });
    }, 2500);
});

// Clear button for filter input
document.addEventListener('DOMContentLoaded', function () {
    const filterInput = document.getElementById('filter-input');
    const filterForm = document.getElementById('filter-form');
    const clearBtn = document.getElementById('clear-filters-btn');
    let debounceTimeout = null;
    let fullReloadTimeout = null;

    function toggleClearButton() {
        if (filterInput.value.trim() !== '') {
            clearBtn.classList.add('visible');
        } else {
            clearBtn.classList.remove('visible');
        }
    }

    if (filterInput && filterForm) {
        toggleClearButton(); // Show/hide on initial load

        filterInput.addEventListener('input', function () {
            toggleClearButton();

            clearTimeout(debounceTimeout);
            clearTimeout(fullReloadTimeout);

            debounceTimeout = setTimeout(() => {
                const formData = new FormData(filterForm);
                formData.set('page', '1');
                const params = new URLSearchParams(formData).toString();
                const url = filterForm.action + '?' + params;

                updateTableContent(url).then(() => {
                    history.pushState({}, '', url);
                    updateExportLinks();
                    filterInput.focus();
                });
            }, 600);

            fullReloadTimeout = setTimeout(() => {
                window.location.reload();
            }, 2000);
        });

        filterForm.addEventListener('submit', function (e) {
            e.preventDefault();
        });
    }
});


// Re-attach event listeners when back/forward buttons are used
window.addEventListener('popstate', function() {
    updateTableContent(window.location.href);
    updateExportLinks();
});

// Loader on every page reload
window.addEventListener('beforeunload', function() {
  showLoader();
  // Hide loader if page is still visible after 1.1 second (e.g., for downloads)
  setTimeout(function() {
    if (document.visibilityState === 'visible') {
      hideLoader();
    }
  }, 1100);
});
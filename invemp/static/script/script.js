document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll("table.sortable").forEach(function(table) {
        const ths = table.querySelectorAll("thead th");
        ths.forEach((th, colIndex) => {
            th.addEventListener("click", function() {
                sortTable(table, colIndex);
            });
        });
    });

    function sortTable(table, colIndex) {
        const tbody = table.tBodies[0];
        const rows = Array.from(tbody.rows);
        const isAsc = table.getAttribute("data-sort-col") == colIndex && table.getAttribute("data-sort-dir") == "asc";
        rows.sort((a, b) => {
            let aText = a.cells[colIndex].textContent.trim();
            let bText = b.cells[colIndex].textContent.trim();
            let aNum = parseFloat(aText.replace(/[^0-9.\-]+/g,""));
            let bNum = parseFloat(bText.replace(/[^0-9.\-]+/g,""));
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAsc ? aNum - bNum : bNum - aNum;
            }
            return isAsc ? aText.localeCompare(bText) : bText.localeCompare(aText);
        });
        rows.forEach(row => tbody.appendChild(row));
        table.setAttribute("data-sort-col", colIndex);
        table.setAttribute("data-sort-dir", isAsc ? "desc" : "asc");
        // Remove sort classes from all headers
        const ths = table.querySelectorAll("thead th");
        ths.forEach(th => th.classList.remove("sorted", "asc", "desc"));
        // Add to the sorted header
        ths[colIndex].classList.add("sorted", isAsc ? "desc" : "asc");
    }

    // Show/hide clear button for filter input
    const filterInput = document.getElementById('filter-input');
    const clearBtn = document.getElementById('clear-filters-btn');
    if (filterInput && clearBtn) {
        function toggleClearBtn() {
            if (filterInput.value.length > 0) {
                clearBtn.classList.add('visible');
            } else {
                clearBtn.classList.remove('visible');
            }
        }
        // Initial state
        toggleClearBtn();
        // On input
        filterInput.addEventListener('input', toggleClearBtn);
    }

    // Auto-hide flash messages after 5 seconds
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
    }, 5000);
});

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
    })
    .finally(() => {
        hideLoader();
    });
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
});

// Re-attach event listeners when back/forward buttons are used
window.addEventListener('popstate', function() {
    updateTableContent(window.location.href);
});

// Loader on every page reload
window.addEventListener('beforeunload', function() {
  showLoader();
  // Hide loader if page is still visible after 2 seconds (e.g., for downloads)
  setTimeout(function() {
    if (document.visibilityState === 'visible') {
      hideLoader();
    }
  }, 2000);
});

/*
// Dark mode toggle logic with icon swap
(function() {
  const toggleBtn = document.getElementById('dark-mode-toggle');
  const icon = document.getElementById('dark-mode-icon');
  const html = document.documentElement;
  const darkModeKey = 'invemp-dark-mode';

  // List of icon selectors and their base filenames (without _dark)
  const iconMap = [
    { selector: '#pdf-icon-img', base: 'pdf_icon.svg' },
    { selector: '#qr-icon-img', base: 'qr_code.svg' },
    { selector: '.nav-icon', base: 'manage_accounts.svg', altBase: 'manage_accounts_dark.svg' },
    { selector: '.btn-back-icon', base: 'arrow_back.svg' },
    { selector: '.btn-back-icon2', base: 'arrow_back_2.svg' },
    { selector: '.profile-icon-img', base: 'profile_icon.svg' },
    // Add more selectors and base filenames as needed
  ];

  function swapIcons(dark) {
    iconMap.forEach(({ selector, base, altBase }) => {
      document.querySelectorAll(selector).forEach(img => {
        // Determine the dark variant filename
        let darkSrc = base.replace('.svg', '_dark.svg');
        // If altBase is provided, use it for dark mode
        if (dark && altBase) darkSrc = altBase;
        // Get current src filename
        const src = img.getAttribute('src');
        if (dark) {
          if (!src.endsWith('_dark.svg')) {
            img.setAttribute('src', src.replace(base, darkSrc));
          }
        } else {
          if (src.endsWith('_dark.svg')) {
            img.setAttribute('src', src.replace('_dark.svg', '.svg'));
          }
        }
      });
    });
  }

  function setDarkMode(on) {
    if (on) {
      html.classList.add('dark-mode');
      icon.textContent = '☀️';
      swapIcons(true);
    } else {
      html.classList.remove('dark-mode');
      icon.textContent = '🌙';
      swapIcons(false);
    }
    localStorage.setItem(darkModeKey, on ? '1' : '0');
  }

  // Restore preference
  const saved = localStorage.getItem(darkModeKey);
  if (saved === '1' || (saved === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    setDarkMode(true);
  } else {
    setDarkMode(false);
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function() {
      setDarkMode(!html.classList.contains('dark-mode'));
    });
  }
})();
*/

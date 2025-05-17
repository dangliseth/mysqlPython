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
      if (!confirm('Are you sure you want to delete this entry along with its history? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });
});

document.addEventListener('DOMContentLoaded', function() {
  const filterInput = document.getElementById('filter-input');
  const filterForm = document.getElementById('filter-form');
  let debounceTimeout = null;

  if (filterInput && filterForm) {
    filterInput.addEventListener('input', function(e) {
      clearTimeout(debounceTimeout);
      debounceTimeout = setTimeout(() => {
        // Use AJAX to submit the form and update the table
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData).toString();
        fetch(filterForm.action + '?' + params, {
          method: 'GET',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        })
        .then(response => response.text())
        .then(html => {
          // Parse the returned HTML and replace the table
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
          // Re-focus the input
          filterInput.focus();
        });
      }, 300); // 300ms debounce
    });
    // Prevent default form submit
    filterForm.addEventListener('submit', function(e) {
      e.preventDefault();
    });
  }
});

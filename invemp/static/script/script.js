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
});
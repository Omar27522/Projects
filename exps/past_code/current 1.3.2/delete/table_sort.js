function sortTable(n) {
    const table = document.querySelector('.monthly-table');
    const tbody = table.querySelector('tbody') || table;
    const rows = Array.from(tbody.querySelectorAll('tr:not(.total-row)'));
    const totalRow = tbody.querySelector('.total-row');
    const headerRow = table.querySelector('thead tr'); // Use thead for headers if possible

    const sortDirection = headerRow.children[n].getAttribute('data-sort') === 'asc' ? 'desc' : 'asc';

    // Update sort indicators
    headerRow.querySelectorAll('th').forEach((th, index) => {
        if (index === n) {
            th.setAttribute('data-sort', sortDirection);
        } else {
            th.removeAttribute('data-sort');
        }
    });

    // Sort rows
    rows.sort((a, b) => {
        let x = a.getElementsByTagName("td")[n].textContent.trim();
        let y = b.getElementsByTagName("td")[n].textContent.trim();

        // Handle date sorting
        if (n === 0) {
            x = new Date(x).getTime() || 0;
            y = new Date(y).getTime() || 0;
        }
        // Handle amount sorting
        else if (n === 4) {
            x = Number.parseFloat(x.replace(/[$,]/g, '')) || 0;
            y = Number.parseFloat(y.replace(/[$,]/g, '')) || 0;
        }

        // String comparison for other columns
        if (typeof x === 'string') {
            return sortDirection === 'asc' 
                ? x.localeCompare(y)
                : y.localeCompare(x);
        }

        // Numeric comparison
        return sortDirection === 'asc' ? x - y : y - x;
    });

    // Clear and rebuild tbody
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    for (const row of rows) {
        tbody.appendChild(row);
    }
    if (totalRow) tbody.appendChild(totalRow); // Append total row at the end
}

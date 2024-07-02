function sortTable(columnIndex) {
    var table = document.getElementById("children-table");
    var rows = Array.prototype.slice.call(table.rows, 1);
    var ascending = table.dataset.sortOrder === 'asc';
    rows.sort(function(rowA, rowB) {
        var cellA = rowA.cells[columnIndex].textContent.trim().toLowerCase();
        var cellB = rowB.cells[columnIndex].textContent.trim().toLowerCase();
        if (cellA < cellB) {
            return ascending ? -1 : 1;
        }
        if (cellA > cellB) {
            return ascending ? 1 : -1;
        }
        return 0;
    });
    table.tBodies[0].append(...rows);
    table.dataset.sortOrder = ascending ? 'desc' : 'asc';
}

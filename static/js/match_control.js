document.querySelectorAll('.table-match').forEach(table => {
    table.addEventListener('click', function() {
        window.location.href = `/match/${this.id}`;
    });
});
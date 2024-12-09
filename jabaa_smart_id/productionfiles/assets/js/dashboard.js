// Toggle Theme Functionality
function toggleTheme() {
  document.body.classList.toggle("dark-mode");
}

// Initialize DataTables
$(document).ready(function () {
  $("#dataTable").DataTable({
    paging: true,
    searching: true,
    lengthChange: true,
    pageLength: 5, // Number of rows per page
    info: false,
  });
});

// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable({
    "columnDefs": [
      {"width": "5%", "targets": [1, 2]}
    ],
    "paging": false
  });
});

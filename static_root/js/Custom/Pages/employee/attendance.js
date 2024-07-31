
$(document).ready(function () {
    $('#leaveDataTable').DataTable({
        dom:'ftlp',
        responsive: true,
        searching: true,
        paging: true,
        fixedHeader: true,
        screenX:true,
    });
    
   
    const csrftoken = document.cookie.match(/csrftoken=([^ ;]+)/)[1];
    $(document).on("click", ".delete-button", function () {
        // Retrieve the value of data-leave-id attribute
        var leaveId = $(this).data("leave-id");
        $('#confirmDeletehidden').val(leaveId);
      });
      
    $('#confirmDelete').on('click', function() {
        var hiddenleaveId = $('#confirmDeletehidden').val();
        // Make an AJAX request to delete the LeaveApplication object
        $.ajax({
            url: '/employee/delete_leave/' + hiddenleaveId + '/',
            data: {},
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
            success: function(response) {
                // Optionally, you can handle a successful response here
                 window.location.reload();
                console.log('Leave deleted successfully');
            },
            error: function(xhr, status, error) {
                // Handle errors
                console.error('Error deleting leave:', xhr.responseText);
            },
            complete: function() {
                // Close the modal
                $('#popupfordelete').modal('hide');
            }
        });
    });
});

$(document).ready(function () {
    $('#RegularizationDataTable').DataTable({
        dom:'ftlp',
        responsive: true,
        searching: true,
        paging: true,
        fixedHeader: true,
        screenX:true,
    });
    $('#DailyAttendanceDataTable').DataTable({
        dom:'ftlp',
        responsive: true,
        searching: true,
        paging: true,
        fixedHeader: true,
        screenX:true,
    });
});
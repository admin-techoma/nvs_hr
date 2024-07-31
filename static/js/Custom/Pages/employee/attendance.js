
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
                // Ensure CSRF token is available
    // Function to format date from 'd-m-Y' to 'Y-m-d'
    function formatDate(dateString) {
        const date = new Date(dateString);
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0'); // Month is zero-based
        const year = date.getFullYear();
        return `${year}-${month}-${day}`;
    }

    // When the edit button is clicked, populate the hidden fields in the modal
    $(document).on('click', '.edit-attendance-btn', function() {
        const employeeId = $(this).data('employee-id');
        const selectedDate = $(this).data('date');
        const formattedDate = formatDate(selectedDate);
        $('#employee_id_hidden').val(employeeId);
        $('#currenthiddendate').val(formattedDate);
    });

    // Handle save attendance button click
    $('#saveAttendance').on('click', function () {
        const selectedDate = $('#currenthiddendate').val();
        const employeeId = $('#employee_id_hidden').val();
        const punchInTime = $('#Punch_In').val();
        const punchOutTime = $('#Punch_Out').val();
        const csrftoken = document.cookie.match(/csrftoken=([^ ;]+)/)[1];
        // Ensure punchInTime and punchOutTime are not empty before saving
        if (punchInTime && punchOutTime) {
            $.ajax({
                url: `/hr/ajax_save_attendance/${employeeId}/${selectedDate}/`,
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    punch_in: punchInTime,
                    punch_out: punchOutTime
                },
                success: function(response) {
                    window.location.reload();
                },
                error: function (xhr, status, error) {
                    const errorMessage = JSON.parse(xhr.responseText).error;
                    $('#errorMessage').text('Error: ' + errorMessage);
                    $('#messageModal').modal('show');
                    $('#attendancemodal').modal('hide');
                }
            });
        } else {
            $('#errorMessage').text('Error: Punch in and Punch out times cannot be empty');
            $('#messageModal').modal('show');
            $('#attendancemodal').modal('hide');
        }
    });
});
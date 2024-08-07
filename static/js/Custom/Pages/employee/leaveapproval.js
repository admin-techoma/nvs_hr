$(document).ready(function() {

    $('#leaveApprovalTable').DataTable({
        responsive: true,
        searching: true,
        paging: true,
        fixedHeader: true,
        lengthMenu:[5,10,15],
        initComplete: function () {
            let api = this.api();
     
            api.on('click', 'tbody td .status-select', function () {
                // console.log("abc");
                $('.status-select').on('change', function() {
                    var selectedStatus = $(this).val();
                    var leaveId = $(this).closest('tr').find('input[type="hidden"]').val();
                    var remarks =$('#remarks_'+leaveId).val();
                    const csrftoken = document.cookie.match(/csrftoken=([^ ;]+)/)[1];
            
                    $.ajax({
                        type: 'POST',
                        url: '/employee/update_leave_status/',  // Replace with your Django URL
                        headers: { 'X-CSRFToken': csrftoken },
                        data: {
                            'leave_id': leaveId,
                            'selected_status': selectedStatus,
                            'remarks':remarks
                        },
                        success: function(response) {
                            // Handle success response
                            $('#modalContent').text(response.success || response.error);
                            $('#responseModal').modal('show');
                        }
                    });
                });
            });
    }
});
    $('#responseModal').on('hidden.bs.modal', function () {
        location.reload();
    });
});
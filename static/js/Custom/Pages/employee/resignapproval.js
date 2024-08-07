$(document).ready(function() {
    $('#ResignationApprovalTable').DataTable({
        responsive: true,
        searching: true,
        paging: true,
        fixedHeader: true,
    });

    $('.status-select').on('change', function() {
        var selectedStatus = $(this).val();
        var row = $(this).closest('tr');
        var resignId = $(this).data('resign-id');
        var remarks = $('#remarks_' + resignId).val();
        var lastDateInput = $('#last_date_input_' + resignId);
        var lastDateLabel = $('#last_date_' + resignId);
        var resignDateLabel = $('#resign_date_' + resignId);

        if (selectedStatus == '1') {  // If status is Approved
            var resignDate = new Date(resignDateLabel.text());
            resignDate.setDate(resignDate.getDate() + 30);
            var formattedDate = resignDate.toISOString().slice(0, 10);

            lastDateLabel.text(formattedDate);
            lastDateInput.val(formattedDate);
            lastDateInput.hide();
            lastDateLabel.show();
        } else {
            lastDateLabel.hide();
            resignDateLabel.show();
        }

        const csrftoken = document.cookie.match(/csrftoken=([^ ;]+)/)[1];

        $.ajax({
            type: 'POST',
            url: '/employee/update_resign_status/',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'resign_id': resignId,
                'selected_status': selectedStatus,
                'remarks': remarks,
                'last_date': lastDateInput.val()
            },
            success: function(response) {
                $('#modalContent').text(response.success || response.error);
                $('#responseModal').modal('show');
            },
            error: function(xhr, status, error) {
                console.error('AJAX Error:', status, error);
            }
        });
    });

    $('#responseModal').on('hidden.bs.modal', function () {
        location.reload();
    });
});
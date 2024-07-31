$(document).ready(function() {

    $('#resignApprovalTable').DataTable({
        responsive: true,
        searching: true,
        paging: true,
        fixedHeader: true,
        lengthMenu:[5,10,15],
        initComplete: function () {
            let api = this.api();
     
            api.on('click', 'tbody td .status-select', function () {
                console.log("xyz");

            $('.status-select').on('change', function() {
                var selectedStatus = $(this).val();
                var resignId = $(this).closest('tr').find('input[type="hidden"]').val();
                var remarks = $('#remarks_' + resignId).val();
                var lastDateInput = $(this).closest('tr').find('.last-date-input');
                var lastDateLabel = $('#last_date_' + resignId);
                var resignDateLabel = $('#resign_date_' + resignId);
                
                if (selectedStatus == '1') {  // If status is Approved
                    // Calculate the date 30 days from the resign date
                    var resignDate = new Date(resignDateLabel.text());
                    resignDate.setDate(resignDate.getDate() + 30);
                    console.log("aresign");
                    // Format the date as YYYY-MM-DD
                    var formattedDate = resignDate.toISOString().slice(0, 10);

                    // Set the "Last Date" label to the calculated date
                    lastDateLabel.text(formattedDate);
                    lastDateInput.val(formattedDate);  // Set the input value

                    lastDateInput.hide();  // Hide the input
                    lastDateLabel.show();  // Show the label
                } else {
                    // If status is not Approved, hide the "Last Date" label and show the resign date label
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
                        'last_date': lastDateInput.val()  // Include the Last Date in the data sent to the server
                    },
                    success: function(response) {
                        // Handle success response
                        $('#modalContent').text(response.success || response.error);
                        $('#responseresignModal').modal('show');
                    }
                });
            });
        });
    }
});

            $('#responseresignModal').on('hidden.bs.modal', function () {
                location.reload();
            });
        });

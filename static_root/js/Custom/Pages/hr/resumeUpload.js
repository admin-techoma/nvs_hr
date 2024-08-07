$(document).ready(function () {
    var error_message = $('#errorField').val();
    var errorModal = $('#errorModal');
    
    if (error_message && error_message !== "None") {
        // Show the error modal
        errorModal.show();
    }

    // Close the error alert when the close button is clicked
    $('#closeErrorAlert').click(function () {
        errorModal.hide();
    });
});
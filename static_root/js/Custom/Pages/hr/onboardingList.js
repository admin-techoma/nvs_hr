$(document).ready(function() {

    $('#onboardingTable').DataTable({
        responsive: true,
        searching: true,
        paging: true,
        fixedHeader: true,
    });
    
    // show error pop-up for onboardings page.
    $('[id^="statusLabel"]').on('click', function () {
        // Get the full ID
        var fullId = $(this).attr('id');
        // Extract the part before the underscore
        var candidateId = fullId.split('_')[1];       
        var checkbox = $(this).find('input[type="checkbox"]');
        // Check if the checkbox is disabled
        if (checkbox.is(':disabled')) {
            $('#onboardingAlert').modal('show');
        }
    });

    $('.close-modal').on('click', function () {
        $('#onboardingAlert').modal('hide');
    });

    hideSuccessAlert();

    $('#KYCForm input[type="file"], #AccountDetailsForm input[type="file"], #EducationalDetailsForm input[type="file"]').on('change', function() {
            const file = this.files[0];
            const previewId = $(this).closest('.col-md-12').find('.preview-img').attr('id');
            if (file && previewId) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const previewObject = $('#previewObject');
                    const fileData = event.target.result;
                    const extension = file.name.split('.').pop().toLowerCase();
                    previewObject.attr('data-extension', extension);
                    if (extension === 'pdf') {
                        $('#' + previewId).attr('src', '/static/admin/img/pdf-svg.svg');
                        $('#' + previewId).addClass('pdf-preview');
                        $('#' + previewId).removeClass('doc-preview');
                        $('#' + previewId).data('fileData', fileData);
                    } else if (extension === 'jpg' || extension === 'jpeg' || extension === 'png') {
                        $('#' + previewId).attr('src', fileData);
                        $('#' + previewId).removeClass('pdf-preview');
                        previewObject.attr('data', ''); // Clear previous data in the modal
                    } else if (extension === 'doc' || extension === 'docx' || extension === 'undefined') {
                        $('#' + previewId).attr('src', '/static/admin/img/doc-svg.svg');
                        $('#' + previewId).removeClass('pdf-preview');
                        $('#' + previewId).addClass('doc-preview');
                    } else {
                        const previewObject = $('#previewObjectModal');
                        const modalBody = previewObject.find('.modal-body');
                        const error = 'Only PDF, DOC, DOCX, JPG, JPEG, and PNG files are allowed.';
                        previewObject.find('.modal-body').empty();
                        modalBody.empty().append(error);
                        $('#previewObjectModal').modal('show');  
                    }
                    $('#previewObject').attr('data-extension', extension);
                };
                reader.readAsDataURL(file);
            } else {
                $('#' + previewId).attr('src', '');
                $('#previewObject').attr('data-extension', ''); // Clear previous data in the modal
            }
        });

    $(document).on('click', '.pdf-preview, .doc-preview', function()
    {
        const previewObject = $('#previewObjectModal');
        const modalBody = previewObject.find('.modal-body');
        const fileData = $(this).data('fileData');
        const extension = $('#previewObject').attr('data-extension');

        if (extension === 'doc' || extension === 'docx' || extension === 'undefined') {
            previewObject.find('.modal-body').empty();
            const error = `This format doesn't support preview mode.`;
            modalBody.empty().append(error);
            $('#previewObject').attr('data', fileData);
            $('#previewObjectModal').modal('show');  
        }
        else{
            previewObject.find('.modal-body').empty();
            previewObject.find('.modal-body').append(`<object id="previewObject" data-extension="${extension}" type="application/pdf" width="100%" height="600px"></object>`);
            $('#previewObject').attr('data', fileData);
            $('#previewObjectModal').modal('show'); 
        }
    });

    $(document).on('click', '.emptyPreview', function()
    {
        const previewObject = $('.modal-content');
        previewObject.attr('data', ''); // Assuming previewObject is the modal element
        previewObject.find('.modal-body').empty();
    });

});

function hideSuccessAlert() {
    setTimeout(function() {
        $('.alert-success').alert('close'); // Close the alert with the 'alert-success' class
        $('.alert-danger').alert('close'); // Close the alert with the 'alert-success' class
    }, 5000); // 5000 milliseconds = 5 seconds
}
        
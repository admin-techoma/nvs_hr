$(document).ready(function () {
    // Initialize DataTable only if it hasn't been initialized yet
    if (!$.fn.DataTable.isDataTable('#resumeListTable')) {
        $('#resumeListTable').DataTable({
            responsive: true,
            searching: true,
            paging: true,
            fixedHeader: true,
        });
    }

    function openEditPopup(resumeId) {
        const currentLocation = window.location.pathname;
        $.ajax({
            url: `/hr/resumes/edit/${resumeId}/`,
            type: 'GET',
            success: function (htmlContent) {
                $("#editModal .modal-body").html(htmlContent);
                $("#editModal").modal("show");

                $("#editModal form").submit(function (e) {
                    e.preventDefault();
                    const formData = new FormData(this);

                    $.ajax({
                        url: `/hr/resumes/edit/${resumeId}/`,
                        type: 'POST',
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function (response) {
                            $('#candidatesuccessModal').modal('show');

                            setTimeout(function () {
                                location.reload(); // Reload the page
                            }, 2000); // 2000 milliseconds = 2 seconds
            
                        },
                        error: function (error) {
                            console.error('Error:', error);
                        }
                    });
                });
            },
            error: function (error) {
                console.error('Error:', error);
            }
        });
    }



    $('.resume-row').on('click', function () {
        var resumeId = $(this).data('resume-id');
        openEditPopup(resumeId);
    });


    $('.btn-close').on('click', function () {
        $("#editModal").modal("hide");
    });

    $('#uploadResumeModalbutton').on('click', function () {
        var uploadUrl = '/hr/upload_resume/';
        $.ajax({
            type: "GET",
            url: uploadUrl,
            success: function (response) {
                $("#uploadResumeModal .modal-body").html(response);
                $("#uploadResumeModal").modal("show");
                $('#uploadResumeForm').on('submit', function (event) {
                    event.preventDefault();
                    var formData = new FormData($(this)[0]);
                    $.ajax({
                        type: "POST",
                        url: uploadUrl,
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function (data) {
                            $('#candidatesuccessModal').modal('show');

                            setTimeout(function () {
                                location.reload(); // Reload the page
                            }, 2000); // 2000 milliseconds = 2 seconds
                        },
                        error: function (xhr, status, error) {
                            $("#uploadResumeModal .modal-body").html('<div class="alert alert-danger">' + xhr.responseJSON.error + '</div>');
                        }
                    });
                });
            }
        });
    });
});

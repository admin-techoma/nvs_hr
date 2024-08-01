$(document).ready(function () {

    alerttimeout();
    $('#interviews_table').DataTable({
        responsive: true,
        searching: true,
        paging: true,
        scrollX: true,
        scrollY: '200px',
        fixedHeader: true,
        language: {
            emptyTable: "No interviews are scheduled yet!"
        }
    });

  

    // Attach the openPreviewPopup function to the click event of elements with the class "preview-link"
    $('.preview-link').on('click', function (e) {
        e.preventDefault(); // Prevent the default behavior of the anchor tag
        openPreviewPopup($(this).data('resume-id'));
    });

    $('.interviewmodeLink').hide();
    $('#id_interviewMode').change(function () {
        // Get the selected option value
        var selectedOption = $(this).val();

        // Check if the selected option is 'online'
        if (selectedOption === 'Online') {
            // Show the element with the class 'interviewmodeLink'
            $('.interviewmodeLink').show();
        } else {
            // Hide the element with the class 'interviewmodeLink'
            $('.interviewmodeLink').hide();
        }
    });

    $("#designationoptions").change(function () {
        var selectedText = $(this).find("option:selected").text();
        $("#hiddendesignationoptions").val(selectedText);
    });

    function openEditPopup(resumeId) {
        const currentLocation = window.location.pathname;
        // Make an AJAX request to fetch the edit form content
        $.ajax({
            url: `/hr/resumes/edit/${resumeId}/`,
            type: 'GET',
            success: function (htmlContent) {
                // Load the content into the modal
                $("#editModal .modal-body").html(htmlContent);
                $("#editModal").modal("show");

                // Attach a submit handler to the form in the modal
                $("#editModal form").submit(function (e) {
                    e.preventDefault(); // Prevent the default form submission
                    const formData = new FormData(this);

                    $.ajax({
                        url: `/hr/resumes/edit/${resumeId}/`, // Ensure this URL is correct
                        type: 'POST',
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function (response) {
                            // Default behavior: close the modal without redirection
                            window.location.href = '/hr/resumes/';
                        },
                        error: function (error) {
                            // Handle any errors, e.g., display an error message
                            console.error('Error:', error);
                        }
                    });
                });
            },
            error: function (error) {
                // Handle any errors, e.g., display an error message
                console.error('Error:', error);
            }
        });
    }


    $('.edit-resume').on('click', function () {
        var resumeId = $(this).attr('id').replace('resumeEdit', '');
        openEditPopup(resumeId);
    });

    $('.btn-close').on('click', function () {
        $("#editModal").modal("hide");
        $('.alert-success').alert('close');
    });

    $('#uploadNewResume').click(function () {
        $('#uploadResumeModal').modal('show');
    });

    $('.close').click(function () {
        $('.modal').modal('hide');
    });

    // Handle form submission with AJAX for upload Resume
    $('#uploadResumeForm').submit(function (e) {
        e.preventDefault();
        var formData = new FormData(this);

        $.ajax({
            type: 'POST',
            url: `{% url 'hr:upload_resume' %}`,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    // Handle success (e.g., close the modal)
                    $('#uploadResumeModal').modal('hide');
                    location.reload();
                } else {
                    // Display error message
                    $('#candidateStatus').html('<div class="alert alert-danger" role="alert">' + response.error + '</div>');
                }
            },
            error: function (xhr, status, error) {
                console.error(error);
            }
        });
    });

    //It opens Interview Invitation Modal
    $('#createInterview').click(function () {
        $('#createInterviewModal').modal('show');
    });

    $('#createInterviewForm').submit(function (e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            type: 'POST',
            url: `/hr/create-interview/`,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {}
        });
    });

    $('#interviewFeedbackForm').submit(function (e) {
        e.preventDefault(); // Prevent the default form submission
        var interviewFeedbackId = $('#interviewFeedbackId').val();
        // Submit the interviewFeedbackForm
        $.ajax({
            type: 'POST',
            url: `/hr/save-interview-feedback/${interviewFeedbackId}/`,
            data: $('#interviewFeedbackForm').serialize(),
            success: function (data) {
                if (data.success) {
                    // Display the success message in your HTML template
                    $('.alert-success').remove(); // Remove previous success messages
                    var successMessage = ' <div class="alert alert-success" role="alert"><div class="row"><div class="col-10 form-group">Candidate status has been changed.</div><div class="col-2 form-group d-flex justify-content-end"><button type="button" class="btn-close close-success" data-bs-dismiss="alert" aria-label="Close"></button></div></div></div>';
                    $('html, body').animate({
                        scrollTop: 0
                    }, 'slow');
                    $('#alert-container').append(successMessage);
                    alerttimeout()
                } else {
                    // Handle other success conditions or error responses
                    alert(data.message);
                }
            }
        });
    });

    $("#departmentoptions").change(function () {
        var id = $(this).val();
        var designationSelect = $("#designationoptions");
        
        $.ajax({
            url: "/hr/ajax/load_designation/",
            data: {
                'department': id
            },
            success: function (data) {
                designationSelect.empty(); // Clear existing options
                designationSelect.append(
                    $("<option>").attr('value', '').text('Select Designation')
                );
    
                var designations = data.designations;
                for (var i = 0; i < designations.length; i++) {
                    designationSelect.append(
                        $("<option>").attr('value', designations[i].id).text(designations[i].name)
                    );
                }
    
            }
        });
    });

    $("#id_interviewRound").change(function () {
        var interviewRound = $(this).val(); // Get the selected interview round
        var departmentId = $("#departmentoptions").val(); // Get the selected department ID
        var interviewerSelect = $("#intervieweroptions");
    
        $.ajax({
            url: "/hr/ajax/load_interviewer/",
            data: {
                'department_id': departmentId,
                'interview_round': interviewRound
            },
            success: function (data) {
                interviewerSelect.empty(); // Clear existing options
                interviewerSelect.append(
                    $("<option>").attr('value', '').text('Select Interviewer')
                );
    
                var interviewers = data.interviewers; // Ensure the key name matches what's returned by the view
                for (var i = 0; i < interviewers.length; i++) {
                    interviewerSelect.append(
                        $("<option>").attr('value', interviewers[i].emp_id+'~'+interviewers[i].email+ '~' + interviewers[i].name).text(interviewers[i].name)
                   
                    );
                }
            }
        });
    });
});


function alerttimeout() {
    // Select all alerts with the class 'alert' that have the data-bs-dismiss attribute to hide alert after 5 sec.
    var alerts = $('.alert');
    // Loop through the alerts
    alerts.each(function () {
        // Set a timeout to close each alert after 5 seconds (5000 milliseconds)
        var alert = $(this);
        setTimeout(function () {
            alert.hide();
        }, 5000);
    });
}

function scheduleInterview(candidateId) {
    // Get the URL for the "scheduleInterview" view using the data-url attribute
    const url = document.getElementById("interviewSchedlue" + candidateId).getAttribute("data-url");

    // Redirect to the "scheduleInterview" view
    window.location.href = url;
}

function openPreviewPopup(resumeId) {
    // Make an AJAX request to fetch the HTML content
    $.ajax({
        url: `/hr/resumes/preview/${resumeId}/`,
        type: 'GET',
        success: function (data) {

            if (data.error) {

                // Display the error message to the user
                alert("Error: " + data.error);
            } else {
                // Create a new browser window
                const newWindow = window.open('', '', 'width=800,height=600');
                // Write the HTML content to the new window
                newWindow.document.open();
                newWindow.document.write(data);
                newWindow.document.close();
            }
        },
        error: function (xhr, status, error) {
            $('#errorModal').modal('show');
        }
    });

    
}





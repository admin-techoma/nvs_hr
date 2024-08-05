$(document).ready(function () {
    const employee = $('#hiddenSession').val();
    let clockInTime = $('#clockInTime').val();

    function getCSRFToken() {
        return document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
    }

    function getCurrentTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    function formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    function calculateElapsedTime() {
        if (!clockInTime) return 0;
        const [clockInHours, clockInMinutes] = clockInTime.split(':').map(Number);
        const clockInDate = new Date();
        clockInDate.setHours(clockInHours, clockInMinutes, 0, 0);

        const currentTime = new Date().getTime();
        const clockIn = clockInDate.getTime();
        const elapsedMilliseconds = currentTime - clockIn;
        return Math.floor(elapsedMilliseconds / 1000);
    }

    function updateWorkedTime() {
        const elapsedSeconds = calculateElapsedTime();
        $('#workHours').text(formatTime(elapsedSeconds));
    }

    function updateTimer() {
        updateWorkedTime();
    }

    function resetDailyWorkHours() {
        clockInTime = null;
        $('#workHours').text('00:00:00');
        if (isClockedIn) {
            isClockedIn = false;
            $('#workHours').css('display', 'none');
        }
    }

    $('#clockedOut').on('click', function () {
        if( /iphone|ipod|ipad|android|blackberry|opera mini|opera mobi|skyfire|maemo|windows phone|palm|iemobile|symbian|symbianos|fennec/i.test(navigator.userAgent) ) {
        $('#ClockoutModal').modal('show');
        $('#ClockoutModal .modal-body span').text(getCurrentTime());

        $('.modal-footer .btn-success').one('click', function () {

            getLocation()
            function getLocation() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(showPosition, showError);
                } else {
                    alert("Geolocation is not supported by this browser.");
                }
            }
            function showPosition(position) {
                $.ajax({
                    url: '/employee/mark-clockOut/' + employee + '/',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    },
                    data: {
                        'latitude': position.coords.latitude,
                        'longitude': position.coords.longitude
                    },
                    success: function (response) {
                        if ('error' in response) {
                            $('#clock_in_Error .modal-body').text(response.error);
                            $('#clock_in_Error').modal('show');
                            return;
                        }
                        isClockedIn = false;
                        $('#workHours').css('display', 'none');
                        $(this).closest('.modal').modal('hide');
                        location.reload();
                    },
                    error: function (xhr, status, error) {
                        console.error(error);
                    }
                });
            }
    
            function showError(error) {
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        alert("User denied the request for Geolocation.");
                        break;
                    case error.POSITION_UNAVAILABLE:
                        alert("Location information is unavailable.");
                        break;
                    case error.TIMEOUT:
                        alert("The request to get user location timed out.");
                        break;
                    case error.UNKNOWN_ERROR:
                        alert("An unknown error occurred.");
                        break;
                }
            }

        });}else{
            window.alert("Use Mobile Device only for punch in");
        }
        

    });
    // $('#clockedIn').on('click', function () {

    //     $('#ClockinModal').modal('show');
    //     $('#ClockinModal .modal-body span').text(getCurrentTime());

    //     $('.modal-footer .btn-success').one('click', function () {
    //         $.ajax({
    //             url: '/employee/mark-clockIn/' + employee + '/',
    //             type: 'POST',
    //             headers: {
    //                 'X-CSRFToken': getCSRFToken()
    //             },
    //             success: function (response) {
    //                 console.log(response);
    //                 if ('error' in response) {
    //                     $('#clock_in_Error .modal-body').text(response.error);
    //                     $('#clock_in_Error').modal('show');
    //                     return;
    //                 }
    //                 clockInTime = getCurrentTime();
    //                 isClockedIn = true;
    //                 $('#workHours').css('display', 'block');
    //                 $(this).closest('.modal').modal('hide');
    //             },
    //             error: function (xhr, status, error) {
    //                 console.error(error);
    //             }
    //         });
    //     });
    // });


    // $('#clockedIn').on('click', function () {
    //     $('#ClockinModal').modal('show');
    //     $('#ClockinModal .modal-body span').text(getCurrentTime());
    
    //     $('.modal-footer .btn-success').one('click', function () {
    //         $.ajax({
    //             url: '/employee/mark-clockIn/' + employee + '/',
    //             type: 'POST',
    //             headers: {
    //                 'X-CSRFToken': getCSRFToken()
    //             },
    //             success: function (response) {
    //                 console.log(response);
    //                 if ('error' in response) {
    //                     $('#clock_in_Error .modal-body').text(response.error);
    //                     $('#clock_in_Error').modal('show');
    //                     return;
    //                 }
    //                 clockInTime = getCurrentTime();
    //                 isClockedIn = true;
    //                 $('#workHours').css('display', 'block');
    //                 $('#ClockinModal').modal('hide'); // Use the modal ID to ensure the correct modal is hidden
    //             },
    //             error: function (xhr, status, error) {
    //                 console.error(error);
    //             }
    //         });
    //     });
    // });
    
    $('#clockedIn').on('click', function () {
        if ( /iphone|ipod|ipad|android|blackberry|opera mini|opera mobi|skyfire|maemo|windows phone|palm|iemobile|symbian|symbianos|fennec/i.test(navigator.userAgent)) {
            $('#ClockinModal').modal('show');
        $('#ClockinModal .modal-body span').text(getCurrentTime());
            
        $('.modal-footer .btn-success').on('click', function () {
            getLocation()
            function getLocation() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(showPosition, showError);
                } else {
                    alert("Geolocation is not supported by this browser.");
                }
            }
    
            function showPosition(position) {
                $.ajax({
                    url: '/employee/mark-clockIn/' + employee + '/',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    },
                    data: {
                        'latitude': position.coords.latitude,
                        'longitude': position.coords.longitude
                    },
                    success: function (response) {
                        console.log(response);
                        if ('error' in response) {
                            $('#clock_in_Error .modal-body').text(response.error);
                            $('#clock_in_Error').modal('show');
                            return;
                        }
                        clockInTime = getCurrentTime();
                        isClockedIn = true;
                        $('#workHours').css('display', 'block');
                        $('#ClockinModal').modal('hide'); // Use the modal ID to ensure the correct modal is hidden
                        location.reload();
                    },
                    error: function (xhr, status, error) {
                        console.error(error);
                    }
                });
            }
    
            function showError(error) {
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        alert("User denied the request for Geolocation.");
                        break;
                    case error.POSITION_UNAVAILABLE:
                        alert("Location information is unavailable.");
                        break;
                    case error.TIMEOUT:
                        alert("The request to get user location timed out.");
                        break;
                    case error.UNKNOWN_ERROR:
                        alert("An unknown error occurred.");
                        break;
                }
            }
    
        });


        }
        else{
            window.alert("Use Mobile Device only for punch in");
        }
        
    });

    setInterval(updateTimer, 1000);

    setInterval(function () {
        const currentTime = new Date();
        const hours = currentTime.getHours();
        const minutes = currentTime.getMinutes();
        if (hours === 0 && minutes === 0) {
            resetDailyWorkHours();
        }
    }, 60000);
    var currentURL = window.location.href;
    // var headerTitle = '';
    // if (currentURL.includes('hr/resumes/')) {
    //     headerTitle = 'Recruitment';
    // }
    // else if (currentURL.includes('hr/schedule-interview/')) {
    //     headerTitle = 'Recruitment < Interview Schedule';
    // }
    // else if (currentURL.includes('hr/track-interviews/')) {
    //     headerTitle = 'Recruitment < Interview Tracker';
    // }
    // else if (currentURL.includes('hr/onboardings/')) {
    //     headerTitle = 'Onboarding';
    // }
    // else if (currentURL.includes('hr/view_documents/')) {
    //     headerTitle = 'Onboarding > View Documents';
    // }
    // else if (currentURL.includes('hr/onboarding-process/')) {
    //     headerTitle = 'Onboarding > Upload Documents';
    // }
    // else if (currentURL.includes('hr/view_employee/')) {
    //     headerTitle = 'Employee';
    // }
    // else if (currentURL.includes('hr/employee_profile/')) {
    //     headerTitle = 'Employee > Employee Profile';
    // }
    // else if (currentURL.includes('hr/edit_employee/')) {
    //     headerTitle = 'Employee > Edit Employee Profile';
    // }
    // else if (currentURL.includes('hr/attendance/')) {
    //     headerTitle = 'attendance';
    // }
    // else if (currentURL.includes('hr/view-attendance/')) {
    //     headerTitle = 'Manage attendance';
    // }
    // else if (currentURL.includes('hr/attendance-report/')) {
    //     headerTitle = 'Manage attendance < Attendance Report';
    // }
    // else if (currentURL.includes('employee/attendance/')) {
    //     headerTitle = 'attendance';
    // }
    // else if (currentURL.includes('employee/leave_approvals/')) {
    //     headerTitle = 'Leave Management';
    // }
    // else if (currentURL.includes('payroll/view_payrolllist/')) {
    //     headerTitle = 'Payroll';
    // }
    // else if (currentURL.includes('payroll/view_payroll/')) {
    //     headerTitle = 'Payroll < View Payroll';
    // }
    // else if (currentURL.includes('payroll/edit_payroll/')) {
    //     headerTitle = 'Payroll < Edit Payroll';
    // }
    // else if (currentURL.includes('payroll/month_salary/')) {
    //     headerTitle = 'Payroll < Month Salary';
    // }
    // else if (currentURL.includes('payroll/view_beforegenerate_salary/')) {
    //     headerTitle = 'Payroll < Month Salary < View Before Generate Salary';
    // }
    // else if (currentURL.includes('payroll/view_generatesalary/')) {
    //     headerTitle = 'Salary';
    // }
    // else if (currentURL.includes('payroll/view_salary/')) {
    //     headerTitle = 'Salary < View Salary';
    // }
    // else if (currentURL.includes('payroll/edit_salary/')) {
    //     headerTitle = 'Salary < Edit Salary';
    // } else if (currentURL.includes('employee/leaves_lists')) {
    //     headerTitle = 'Leave Approvals';
    // }
    // else if (currentURL.includes('employee/resign_lists/')) {
    //     headerTitle = 'Resignation Approvals';
    // }
    // else if (currentURL.includes('report/employee_report/')) {
    //     headerTitle = 'Report > Employee Report';
    // }
    // else if (currentURL.includes('report/track-interviewsreport/')) {
    //     headerTitle = 'Report > Track Interviews Report';
    // }

    // else if (currentURL.includes('report/interviews_report/')) {
    //     headerTitle = 'Report > Interviews Report';
    // }
    // else if (currentURL.includes('report/onboarding_report/')) {
    //     headerTitle = 'Report > Onboarding Report';
    // }
    // else if (currentURL.includes('report/attendance_report/')) {
    //     headerTitle = 'Report > Attendance Report';
    // }
    // else if (currentURL.includes('/report/leave_report/')) {
    //     headerTitle = 'Report > Leave Report';
    // }
    // else if (currentURL.includes('/report/view_payrollreport/')) {
    //     headerTitle = 'Report > Payroll Report';
    // }
    // else if (currentURL.includes('/report/salary_report/')) {
    //     headerTitle = 'Report > Salary Report';
    // }
    // else if (currentURL.includes('/report/resign_report/')) {
    //     headerTitle = 'Report > Resignation Report';
    // }
    // else if (currentURL.includes('/report/document_report/')) {
    //     headerTitle = 'Report > Document Report';
    // }
    // else if (currentURL.includes('hr/hr_dashboard')) {
    //     headerTitle = 'Dashboard';
    // }
    // else if (currentURL.includes('adminhrmodule/dash')) {
    //     headerTitle = 'Dashboard';
    // }
    // else if (currentURL.includes('employee/dash')) {
    //     headerTitle = 'Dashboard';
    // }
    // else if (currentURL.includes('employee/view_payroll')) {
    //     headerTitle = 'Payroll';
    // }
    // else if (currentURL.includes('employee/view_profile')) {
    //     headerTitle = 'My Profile';
    // }
    // else if (currentURL.includes('employee/password_change')) {
    //     headerTitle = 'Password Change';
    // }
    // // Update the header title
    // $('.headertitle h4').text(headerTitle);
    // // Add click event for 'Interview List'
    // if (headerTitle.includes('Recruitment')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/interviews/' when 'Interview List' is clicked
    //         window.location.href = '/hr/resumes/';
    //     });
    // }
    // // Add click event for 'Onboarding'
    // if (headerTitle.includes('Onboarding')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/hr/onboardings/';
    //     });
    // }
    // // Add click event for 'Onboarding'
    // if (headerTitle.includes('Employee')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/hr/view_employee/';
    //     });
    // }
    // // Add click event for 'Onboarding'
    // if (headerTitle.includes('Manage')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/hr/view-attendance/';
    //     });
    // }
    // // Add click event for 'Onboarding'
    // if (headerTitle.includes('Payroll')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/payroll/view_payrolllist/';
    //     });
    // }
    // // Add click event for 'Onboarding'
    // if (headerTitle.includes('View Salary')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/payroll/view_generatesalary/';
    //     });
    // }
    // // Add click event for 'Onboarding'
    // if (headerTitle.includes('Edit Salary')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/payroll/view_generatesalary/';
    //     });
    // }
    // // Add click event for 'Report'
    // if (headerTitle.includes('Employee Report')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/report/employee_report/';
    //     });
    // }
    // // Add click event for 'Report'
    // if (headerTitle.includes('Interviews Report')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/report/interviews_report/';
    //     });
    // }
    // // Add click event for 'Report'
    // if (headerTitle.includes('Onboarding Report')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/report/onboarding_report/';
    //     });
    // }
    // // Add click event for 'Report'
    // if (headerTitle.includes('Attendance Report')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/report/attendance_report/';
    //     });
    // }
    // // Add click event for 'Report'
    // if (headerTitle.includes('Leave Report')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/report/leave_report/';
    //     });
    // }
    // // Add click event for 'Report'
    // if (headerTitle.includes('Payroll Report')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/report/view_payrollreport/';
    //     });
    // }
    // // Add click event for 'Report'
    // if (headerTitle.includes('Salary Report')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/report/salary_report/';
    //     });
    // }
    // // Add click event for 'Report'
    // if (headerTitle.includes('Resignation Report')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/report/resign_report/';
    //     });
    // }
    // // Add click event for 'Report'
    // if (headerTitle.includes(' Document Report')) {
    //     $('.headertitle h4').on('click', function () {
    //         // Redirect to 'hr/onboardings/' when 'Onboarding' is clicked
    //         window.location.href = '/report/document_report/';
    //     });
    // }

  
});

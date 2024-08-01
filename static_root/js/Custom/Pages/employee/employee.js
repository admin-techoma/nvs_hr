document.addEventListener('DOMContentLoaded', function () {
    var employeeIdElement = document.getElementById('employeeId');
    var employeeId = employeeIdElement ? employeeIdElement.value : null;

    document.getElementById('paySlipLink')?.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent default link behavior
        window.location.href = '/employee/view_payroll'; 
    });

    document.getElementById('empAttendanceLink')?.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent default link behavior
        window.location.href = '/employee/attendance'; 
    });
    
    // document.getElementById('leaveApprovalLink')?.addEventListener('click', function (e) {
    //     e.preventDefault(); // Prevent default link behavior
    //     if (employeeId !== null) {
    //         window.location.href = '/employee/leaves_lists/' + employeeId;
    //     } else {
    //         console.error('Employee ID is missing.');
    //     }
    // });
});
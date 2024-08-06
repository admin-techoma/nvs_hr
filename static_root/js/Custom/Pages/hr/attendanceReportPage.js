// $(document).ready(function () {

//     $('#attendanceReport').DataTable({
//         responsive: true,
//         searching: true,
//         paging: true,
//         fixedHeader: true,
//     });

//     // $('#leaveDataTable').DataTable({
//     //     responsive: true,
//     //     searching: true,
//     //     paging: true,
//     //     fixedHeader: true,
//     // });
    
//     const csrftoken = document.cookie.match(/csrftoken=([^ ;]+)/)[1];

//     function formatDate(dateString) {
//         const [day, month, year] = dateString.split('-');
//         return `${year}-${month}-${day}`;
//       }

//     $('#saveAttendace').on('click', function () {
//         const selectedDate = $('#currenthiddendate').val();
//         const formattedDate = formatDate(selectedDate);
//         const employeeId = $('#employee_id_hidden').val();
//         const punchInTime = $('#Punch_In').val();
//         const punchOutTime = $('#Punch_Out').val();
      
//         // Make sure punchInTime and punchOutTime are not empty before saving
//           $.ajax({
//             url: `/hr/ajax_save_attendance/${employeeId}/${formattedDate}/`,
//             method: 'POST',
//             headers: { 'X-CSRFToken': csrftoken },
//             data: {
//               punch_in: punchInTime,
//               punch_out: punchOutTime
//             },
//             success: function(response) {
//                 window.location.reload()
//             },
//             error: function (xhr, status, error) {
//                 const errorMessage = JSON.parse(xhr.responseText).error;
//                 $('#errorMessage').text('Error: ' + errorMessage);
//                 $('#messageModal').modal('show');
//                 $('#attendancemodal').modal('hide');

//             }
//           });
//       });
// });
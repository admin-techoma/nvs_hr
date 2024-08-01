// $(document).ready(function() {
//     const daysTag = $(".days");
//     const currentDate = $(".current-date");
//     const prevNextIcon = $(".icons span");
//     var currentUrl = window.location.href;
  
//     if (currentUrl.includes('/hr/employee_profile/')) {
//       var parts = currentUrl.split('/');
//       var employee_Id = parts[parts.length - 2];
//     } else if (currentUrl.includes('/employee/attendance/')) {
//       var employee_Id = $('#hiddenSession').val();
//     }
  
//     const employeeId = employee_Id;
//     $('#employee_id_hidden').val(employeeId);
//     const nationalHolidays = [
//       { date: "14-1-2024", label: "Makarsankranti Day" },
//       { date: "15-1-2024", label: "Makarsankranti Day 2" },
//       { date: "26-1-2024", label: "Republic Day" },
//       { date: "25-3-2024", label: "Holi" },
//       { date: "15-8-2024", label: "Independence Day"},
//       { date: "2-10-2024", label: "Gandhi jayanti"},
//       { date: "12-10-2024", label: "Dussehra" },
//       { date: "31-10-2024", label: "Diwali" },
//       { date: "1-11-2024", label: "Diwali Day 2" },
//       { date: "2-11-2024", label: "Diwali Day 3" },
//       { date: "3-11-2024", label: "Diwali Day 4" },
//       { date: "4-11-2024", label: "Diwali Day 5" },
//       { date: "25-12-2024", label: "Christmas Day" }
//     ];
//     let date = new Date();
//     let currYear = date.getFullYear();
//     let currMonth = date.getMonth();
  
//     const months = [
//       "January", "February", "March", "April", "May", "June", "July",
//       "August", "September", "October", "November", "December"
//     ];
  
//     const renderCalendar = () => {
//       let firstDayofMonth = new Date(currYear, currMonth, 1).getDay();
//       let lastDateofMonth = new Date(currYear, currMonth + 1, 0).getDate();
//       let lastDayofMonth = new Date(currYear, currMonth, lastDateofMonth).getDay();
//       let lastDateofLastMonth = new Date(currYear, currMonth, 0).getDate();
//       let liTag = "";
  
//       for (let i = firstDayofMonth; i > 0; i--) {
//         liTag += `<li class="inactive"> <p>${lastDateofLastMonth - i + 1}</p></li>`;
//       }
  
//       const hiddenInput = $('<input type="hidden" id="currenthiddendate" />');
//       $('.calendar').append(hiddenInput);
  
//       for (let i = 1; i <= lastDateofMonth; i++) {
//         let isToday = i === date.getDate() && currMonth === new Date().getMonth() && currYear === new Date().getFullYear() ? "active" : "";
//         let dataDate = `${i}-${currMonth + 1}-${currYear}`;
//         let holidayClass = "";
  
//         const isNationalHoliday = nationalHolidays.some(holiday => holiday.date === dataDate);
  
//         if (isNationalHoliday) {
//           holidayClass = "national-holiday";
//           liTag += `<li class="${isToday} ${holidayClass}" data-date="${dataDate}" title="${nationalHolidays.find(holiday => holiday.date === dataDate).label}"><p class="holidaydate">${i} </p> <p class="festivalname"
//           >${nationalHolidays.find(holiday => holiday.date === dataDate).label} </p></li>`;
//         } else {
//           let dayOfWeek = new Date(`${currYear}-${currMonth + 1}-${i}`).getDay();
//           if (dayOfWeek === 0) {
//             liTag += `<li class="weekoff" data-date="${dataDate}"><p>${i}</p></li>`;
//           } else {
//             liTag += `<li  class="${isToday}" data-date="${dataDate}"><p>${i}</p></li>`;
//           }
//         }
//       }
  
//       for (let i = lastDayofMonth; i < 6; i++) {
//         const inactiveDate = lastDateofMonth + i - lastDayofMonth + 1;
//         const dataDate = `${inactiveDate}-${currMonth + 1}-${currYear}`;
//         const isNationalHoliday = nationalHolidays.some(holiday => holiday.date === dataDate);
  
//         if (isNationalHoliday) {
//           dayClass = 'national-holiday';
//           liTag += `<li class="inactive ${dayClass}"> <p>${i - lastDayofMonth + 1}</p> </li>`
//         } else {
//           liTag += `<li class="inactive"> <p>${i - lastDayofMonth + 1}</p> </li>`
//         }
//       }
  
//       currentDate.text(`${months[currMonth]} ${currYear}`);
//       daysTag.html(liTag);
      
//       // Calculate and display the number of Sundays
//       const weekoffDays = calculateWeekoffDays(currYear, currMonth);
//       $('#weekoffDays').text(`Weekoff Days: ${weekoffDays}`);
//     }
  
//     const calculateWeekoffDays = (year, month) => {
//       let sundays = 0;
//       let date = new Date(year, month, 1);
//       while (date.getMonth() === month) {
//         if (date.getDay() === 0) { // 0 is Sunday
//           sundays++;
//         }
//         date.setDate(date.getDate() + 1);
//       }
//       return sundays;
//     }
  
//     // $('#attendancemodal').on('click', '#applyForLeave', function() {
//     //   const selectedDate = $('#currenthiddendate').val();
  
//     //   if (selectedDate) {
//     //     const [day, month, year] = selectedDate.split('-');
//     //     const formattedDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
//     //     $('#leavedateFrom').val(formattedDate);
//     //     $('#leavedateTo').val(formattedDate);
//     //   } else {
//     //     console.error('data-date attribute is undefined or empty');
//     //   }
//     // });
  
//     renderCalendar();
  
//     prevNextIcon.each(function() {
//       $(this).on("click", function() {
//         currMonth = this.id === "prev" ? currMonth - 1 : currMonth + 1;
  
//         if (currMonth < 0 || currMonth > 11) {
//           date = new Date(currYear, currMonth, new Date().getDate());
//           currYear = currMonth < 0 ? currYear - 1 : currYear + 1;
//           currMonth = (currMonth + 12) % 12;
//         }
  
//         date = new Date(currYear, currMonth, 1);
  
//         fetchEmployeeAttendance(employeeId);
//         fetchEmployeeLeaveData(employeeId);
//         renderCalendar();
//         updateDataForMonth(currYear, currMonth + 1);
  
//       });
//     });
  
//     const fetchEmployeeAttendance = (employeeId) => {
//       $.ajax({
//         url: `/employee/employee_attendance/${employeeId}/`,
//         method: 'GET',
//         success: function(response) {
//           const attendanceData = response.attendance_data || [];
//           const leaveData = [];
//           updateCalendarWithAttendance(attendanceData, leaveData);
//         },
//         error: function(error) {
//           console.error('Error fetching attendance data:', error);
//           updateCalendarWithAttendance([], []);
//         }
//       });
//     };
  
//     const fetchEmployeeLeaveData = (employeeId) => {
//       $.ajax({
//         url: `/employee/employee_leave_data/${employeeId}/`,
//         method: 'GET',
//         success: function(response) {
//           const leaveData = response.leave_data || [];
//           const attendanceData = [];
//           updateCalendarWithAttendance(attendanceData, leaveData);
//         },
//         error: function(error) {
//           console.error('Error fetching leave data:', error);
//           updateCalendarWithAttendance([], []);
//         }
//       });
//     };
  
//     const updateCalendarWithAttendance = (attendanceData, leaveData) => {
//       const daysClasses = {};
//       const calendarStartDate = new Date(currYear, currMonth, 1);
//       attendanceData.forEach((attendance) => {
//         const clockInDate = new Date(attendance.date);
//         const dayOffset = Math.floor((clockInDate - calendarStartDate) / (24 * 60 * 60 * 1000));
//         const calendarDay = dayOffset + 1;
//         const selector = `.days li[data-date="${calendarDay}-${currMonth + 1}-${currYear}"]`;
//         const $currentLi = $(selector);
//         $currentLi.removeClass('present halfday halfdayapproved absent paidleave');
//         if ($currentLi.length > 0) {
//           if (attendance.is_full_day) {
//             $currentLi.addClass('present');
//           }
//           if (attendance.is_half_day && !$currentLi.hasClass('absent')) {
//             $currentLi.addClass('halfday halfdayapproved');
//           }
//           if (attendance.is_absent) {
//             $currentLi.removeClass('paidleave');
//             $currentLi.addClass('absent');
//           }
//         }
//       });
  
//       leaveData.forEach((leave) => {
//         if (leave.is_approved) {
//           const leaveDate = new Date(leave.date);
//           const dayOffset = Math.floor((leaveDate - calendarStartDate) / (24 * 60 * 60 * 1000));
//           const calendarDay = dayOffset + 1;
//           const selector = `.days li[data-date="${calendarDay}-${currMonth + 1}-${currYear}"]`;
//           const $currentLi = $(selector);
//           $currentLi.removeClass('present halfday halfdayapproved absent');
//           $currentLi.addClass('paidleave');
//         }
//       });
  
//       const calendarDays = $(".days li");
  
//       calendarDays.each(function(index) {
//         const $parentLi = $(this).parent();
//         const isActive = !$parentLi.hasClass('inactive');
  
//         if (isActive) {
//           const dayText = $(this).data('date');
//           const dayClass = daysClasses[dayText];
  
//           if (dayClass) {
//             $parentLi.addClass(dayClass);
//           }
//         }
//       });
//     };
  
//     const updateDataForMonth = (employee_Id, year, month) => {
//       $.ajax({
//         url: `/employee/employee_monthly_data/${employee_Id}/${year}/${month}/`,
//         method: 'GET',
//         dataType: 'json',
//         success: function(response) {
//           if (response && typeof response === 'object') {
//             $('.border-left-green p').text(response.totalPresents || 0);
//             $('.border-left-red p').text(response.totalAbsents || 0);
//             $('.border-left-yellow p').text(response.totalHalfDays || 0);
//             $('.border-left-orange p').text(response.totalPaidLeaves || 0);
//             $('.Leave-Balance p').text(response.totalLeaveBalance || 0);
//             $('.weekoffcard p').text(response.weekoffDays || 0);
//           } else {
//             console.error('Invalid response format:', response);
//           }
//         },
//         error: function(xhr, status, error) {
//           console.error('Error fetching monthly data:', status, error);
//         }
//       });
//     };
  
//     const updateDataForCurrentMonth = (employee_Id) => {
//       updateDataForMonth(employee_Id, currYear, currMonth + 1);
//     };
  
//     fetchEmployeeAttendance(employeeId);
//     fetchEmployeeLeaveData(employeeId);
//     updateDataForCurrentMonth(hiddenSession.value);
//   });
  
//   // Create a container to display the number of weekoff days
//   $('body').append('<div id="weekoffDays"></div>');
  
//   $(document).on('click', '.days li.absent , .days li.halfday' , function() {
//     $('#regularlizationmodal').modal('show');
//   });


$(document).ready(function() {
  const daysTag = $(".days");
  const currentDate = $(".current-date");
  const prevNextIcon = $(".icons span");
  var currentUrl = window.location.href;

  if (currentUrl.includes('/hr/employee_profile/')) {
    var parts = currentUrl.split('/');
    var employee_Id = parts[parts.length - 2];
  } else if (currentUrl.includes('/employee/attendance/')) {
    var employee_Id = $('#hiddenSession').val();
  }
  const employeeId = employee_Id;
  $('#employee_id_hidden').val(employeeId);
  const nationalHolidays = [
    { date: "14-1-2024", label: "Makarsankranti Day" },
    { date: "15-1-2024", label: "Makarsankranti Day 2" },
    { date: "26-1-2024", label: "Republic Day" },
    { date: "25-3-2024", label: "Holi" },
    { date: "15-8-2024", label: "Independence Day" },
    { date: "2-10-2024", label: "Gandhi Jayanti" },
    { date: "12-10-2024", label: "Dussehra" },
    { date: "31-10-2024", label: "Diwali" },
    { date: "1-11-2024", label: "Diwali Day 2" },
    { date: "2-11-2024", label: "Diwali Day 3" },
    { date: "3-11-2024", label: "Diwali Day 4" },
    { date: "4-11-2024", label: "Diwali Day 5" },
    { date: "25-12-2024", label: "Christmas Day" }
  ];
  let date = new Date();
  let currYear = date.getFullYear();
  let currMonth = date.getMonth();

  const months = [
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December"
  ];

  const renderCalendar = () => {
    let firstDayofMonth = new Date(currYear, currMonth, 1).getDay();
    let lastDateofMonth = new Date(currYear, currMonth + 1, 0).getDate();
    let lastDayofMonth = new Date(currYear, currMonth, lastDateofMonth).getDay();
    let lastDateofLastMonth = new Date(currYear, currMonth, 0).getDate();
    let liTag = "";

    for (let i = firstDayofMonth; i > 0; i--) {
      liTag += `<li class="inactive"> <p>${lastDateofLastMonth - i + 1}</p></li>`;
    }

    const hiddenInput = $('<input type="hidden" id="currenthiddendate" />');
    $('.calendar').append(hiddenInput);

    for (let i = 1; i <= lastDateofMonth; i++) {
      let isToday = i === date.getDate() && currMonth === new Date().getMonth() && currYear === new Date().getFullYear() ? "active" : "";
      let dataDate = `${i}-${currMonth + 1}-${currYear}`;
      let holidayClass = "";

      const isNationalHoliday = nationalHolidays.some(holiday => holiday.date === dataDate);

      if (isNationalHoliday) {
        holidayClass = "national-holiday";
        liTag += `<li class="${isToday} ${holidayClass}" data-date="${dataDate}" title="${nationalHolidays.find(holiday => holiday.date === dataDate).label}"><p class="holidaydate">${i} </p> <p class="festivalname"
        >${nationalHolidays.find(holiday => holiday.date === dataDate).label} </p></li>`;
      } else {
        let dayOfWeek = new Date(`${currYear}-${currMonth + 1}-${i}`).getDay();
        if (dayOfWeek === 0) {
          liTag += `<li class="weekoff" data-date="${dataDate}"><p>${i}</p></li>`;
        } else {
          liTag += `<li  class="${isToday}" data-date="${dataDate}"><p>${i}</p></li>`;
        }
      }
    }

    for (let i = lastDayofMonth; i < 6; i++) {
      const inactiveDate = lastDateofMonth + i - lastDayofMonth + 1;
      const dataDate = `${inactiveDate}-${currMonth + 1}-${currYear}`;
      const isNationalHoliday = nationalHolidays.some(holiday => holiday.date === dataDate);

      if (isNationalHoliday) {
        dayClass = 'national-holiday';
        liTag += `<li class="inactive ${dayClass}"> <p>${i - lastDayofMonth + 1}</p> </li>`
      } else {
        liTag += `<li class="inactive"> <p>${i - lastDayofMonth + 1}</p> </li>`
      }
    }

    currentDate.text(`${months[currMonth]} ${currYear}`);
    daysTag.html(liTag);
    
    // Calculate and display the number of Sundays
    const weekoffDays = calculateWeekoffDays(currYear, currMonth);
    $('#weekoffDays').text(`Weekoff Days: ${weekoffDays}`);
  }

  const calculateWeekoffDays = (year, month) => {
    let sundays = 0;
    let date = new Date(year, month, 1);
    while (date.getMonth() === month) {
      if (date.getDay() === 0) { // 0 is Sunday
        sundays++;
      }
      date.setDate(date.getDate() + 1);
    }
    return sundays;
  }

  renderCalendar();

  prevNextIcon.each(function() {
    $(this).on("click", function() {
      currMonth = this.id === "prev" ? currMonth - 1 : currMonth + 1;

      if (currMonth < 0 || currMonth > 11) {
        date = new Date(currYear, currMonth, new Date().getDate());
        currYear = currMonth < 0 ? currYear - 1 : currYear + 1;
        currMonth = (currMonth + 12) % 12;
      }

      date = new Date(currYear, currMonth, 1);

      fetchEmployeeAttendance(employeeId);
      fetchEmployeeLeaveData(employeeId);
      renderCalendar();
      updateDataForMonth(currYear, currMonth + 1);

    });
  });

  const fetchEmployeeAttendance = (employeeId) => {
    $.ajax({
      url: `/employee/employee_attendance/${employeeId}/`,
      method: 'GET',
      success: function(response) {
        const attendanceData = response.attendance_data || [];
        updateCalendarWithAttendance(attendanceData);
      },
      error: function(error) {
        console.error('Error fetching attendance data:', error);
        updateCalendarWithAttendance([]);
      }
    });
  };

  const fetchEmployeeLeaveData = (employeeId) => {
    $.ajax({
      url: `/employee/employee_leave_data/${employeeId}/`,
      method: 'GET',
      success: function(response) {
        const leaveData = response.leave_data || [];
        updateCalendarWithLeave(leaveData);
      },
      error: function(error) {
        console.error('Error fetching leave data:', error);
        updateCalendarWithLeave([]);
      }
    });
  };

  const updateCalendarWithAttendance = (attendanceData) => {
    const calendarStartDate = new Date(currYear, currMonth, 1);
    attendanceData.forEach((attendance) => {
      const attendanceDate = new Date(attendance.date);
      const dayOffset = Math.floor((attendanceDate - calendarStartDate) / (24 * 60 * 60 * 1000));
      const calendarDay = dayOffset + 1;
      const selector = `.days li[data-date="${calendarDay}-${currMonth + 1}-${currYear}"]`;
      const $currentLi = $(selector);
      $currentLi.removeClass('present halfday halfdayapproved absent paidleave');
      if ($currentLi.length > 0) {
        if (attendance.is_full_day) {
          $currentLi.addClass('present');
        }
        if (attendance.is_half_day && !$currentLi.hasClass('absent')) {
          $currentLi.addClass('halfday halfdayapproved');
        }
        if (attendance.is_absent) {
          $currentLi.removeClass('paidleave');
          $currentLi.addClass('absent');
        }
      }
    });

    // Add "onleave" class to days with no class up to the current date
    const today = new Date();
    $('.days li').each(function() {
      const dataDate = $(this).data('date');
      const [day, month, year] = dataDate.split('-').map(Number);
      const dateObj = new Date(year, month - 1, day);
      if (dateObj <= today && !$(this).hasClass('present') && !$(this).hasClass('halfday') && !$(this).hasClass('absent') && !$(this).hasClass('paidleave') && !$(this).hasClass('weekoff') && !$(this).hasClass('national-holiday')) {
        $(this).addClass('onleave');
      }
    });
  };

  const updateCalendarWithLeave = (leaveData) => {
    const calendarStartDate = new Date(currYear, currMonth, 1);
    leaveData.forEach((leave) => {
      const leaveDate = new Date(leave.date);
      if (leave.is_approved) {
        const dayOffset = Math.floor((leaveDate - calendarStartDate) / (24 * 60 * 60 * 1000));
        const calendarDay = dayOffset + 1;
        const selector = `.days li[data-date="${calendarDay}-${currMonth + 1}-${currYear}"]`;
        const $currentLi = $(selector);
        $currentLi.removeClass('present halfday halfdayapproved absent');
        $currentLi.addClass('paidleave onleave');
      }
    });

    // Add "onleave" class to days with no class up to the current date
    const today = new Date();
    $('.days li').each(function() {
      const dataDate = $(this).data('date');
      const [day, month, year] = dataDate.split('-').map(Number);
      const dateObj = new Date(year, month - 1, day);
      if (dateObj <= today && !$(this).hasClass('present') && !$(this).hasClass('halfday') && !$(this).hasClass('absent') && !$(this).hasClass('paidleave') && !$(this).hasClass('weekoff') && !$(this).hasClass('national-holiday')) {
        $(this).addClass('onleave');
      }
    });
  };

  const updateDataForMonth = (employee_Id, year, month) => {
    $.ajax({
      url: `/employee/employee_monthly_data/${employee_Id}/${year}/${month}/`,
      method: 'GET',
      dataType: 'json',
      success: function(response) {
        if (response && typeof response === 'object') {
          $('.border-left-green p').text(response.totalPresents || 0);
          $('.border-left-red p').text(response.totalAbsents || 0);
          $('.border-left-yellow p').text(response.totalHalfDays || 0);
          $('.border-left-orange p').text(response.totalPaidLeaves || 0);
          $('.Leave-Balance p').text(response.totalLeaveBalance || 0);
          $('.weekoffcard p').text(response.weekoffDays || 0);
        } else {
          console.error('Invalid response format:', response);
        }
      },
      error: function(xhr, status, error) {
        console.error('Error fetching monthly data:', status, error);
      }
    });
  };

  const updateDataForCurrentMonth = (employee_Id) => {
    updateDataForMonth(employee_Id, currYear, currMonth + 1);
  };

  fetchEmployeeAttendance(employeeId);
  fetchEmployeeLeaveData(employeeId);
  updateDataForCurrentMonth(hiddenSession.value);
});

// Create a container to display the number of weekoff days
$('body').append('<div id="weekoffDays"></div>');

$(document).on('click', '.days li.absent, .days li.halfday, .days li.onleave', function() {
  $('#regularlizationmodal').modal('show');
});
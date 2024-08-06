self.addEventListener('message', function (event) {
    
    // Function to check if the current time is the desired execution time
    function isExecutionTime(now) {
        const targetTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 20, 0, 0, 0);
        return now >= targetTime;
    }

    // Function to perform the background task
    function performBackgroundTask() {
        const now = new Date();
        const csrfToken = event.data.csrfToken;

        //  console.log('Current Time:', now);

        if (isExecutionTime(now)) {
            //  console.log('Fetching list of employees...');

            fetch('/employee/get_all_employees/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(employees => {
                //  console.log('List of employees:', employees);

                employees.forEach(employee => {
                    //  console.log('Processing employee:', employee);

                    // Check if the employee is absent for today
                    fetch(`/employee/check_attendance/${employee.emp_id}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ date: now.toISOString() })
                    })
                    .then(response => response.json())
                    .then(data => {
                        // console.log('Attendance check successful for employee:', employee.emp_id, data);
                    })
                    .catch(error => {
                        console.error('Attendance check failed for employee:', employee.emp_id, error);
                    });

                    // Check if the employee has an approved leave for today
                    fetch(`/employee/check_leave/${employee.emp_id}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ date: now.toISOString() })
                    })
                    .then(response => response.json())
                    .then(data => {
                        //  console.log('Leave check successful for employee:', employee.emp_id, data);
                    })
                    .catch(error => {
                        // console.error('Leave check failed for employee:', employee.emp_id, error);
                    });
                });

                //  self.postMessage('Task completed');
            })
            .catch(error => {
                console.error('Failed to fetch list of employees:', error);
            });
        }
    }

    // Execute the function every second
    const intervalId = setInterval(performBackgroundTask, 1000);

    // Stop the interval when needed (e.g., when the user logs out)
    // clearInterval(intervalId);
});

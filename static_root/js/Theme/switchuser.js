

    function redirectToDash() {
        // Redirect to the 'dash' URL when the switch is clicked
        window.location.href = "/employee/dash";
    }

    document.addEventListener('DOMContentLoaded', function() {
        // JavaScript code for toggling admin content
        const roleSwitchBtn = document.getElementById('roleSwitchBtn');
        const adminmainwrapper = document.getElementById('adminmainWrapper');
        const mainwrapper = document.getElementById('mainWrapper');

        // Initial role
        let isAdmin = false;

        roleSwitchBtn.addEventListener('click', function() {
            isAdmin = !isAdmin; // Toggle role

            if (isAdmin) {
                adminmainwrapper.style.display = 'block'; // Display admin content
                mainwrapper.style.display = 'none'; // Hide user content
            } else {
                adminmainwrapper.style.display = 'none'; // Hide admin content
                mainwrapper.style.display = 'block'; // Display user content
            }
        });
    });



// // // Function to switch between admin and employee pages
function switchPage() {
    var contentDiv = document.getElementById('mainWrapper');
    var switchButton = document.getElementById('switch-button');

    // Determine the current page based on the query parameter in the URL
    var currentPage = (new URLSearchParams(window.location.search)).get('role');

    // Set initial button text based on the current page
    switchButton.textContent = (currentPage === 'admin') ? 'Switch to Employee' : 'Switch to Admin';

    // Load content based on the current page
    var contentUrl = (currentPage === 'admin') ? 'admin/admin_dashboard' : '../employee/dash';

    // Fetch content from the corresponding URL
    fetch(contentUrl)
      .then(response => response.text())
      .then(data => {
        // Update content
        contentDiv.innerHTML = data;

        // Check if the department is HR or Admin to display sidebar
        var department = '{{ department }}'; // Assuming department is passed as a template variable
        var sidebar = document.getElementById('sidebar');

        // Set the HTML content for the sidebar dynamically
        sidebar.innerHTML = `
          <nav class="overflow-hidden">
            {% with request.resolver_match.url_name as url_name %}
            <ul class="nav  ">
              <li class="nav-item {% if url_name == 'dash' %}active{% endif %}">
                  <a class="nav-link " href="{% url 'employee:dash'  %}">
                      <span class="bi bi-grid nav-icon"></span>
                      <span class="nav-text">Dashboard</span></a>
              </li>
              <li class="nav-item {% if url_name == 'attendance' %}active{% endif %}">
                  <a class="nav-link" href="{% url 'employee:attendance'  %}">
                      <span class="bi bi-p-square nav-icon"></span>
                      <span class="nav-text">Attendance</span></a>
              </li>
              <li class="nav-item {% if url_name == 'view_payroll' %}active{% endif %}">
                  <a class="nav-link" href="{% url 'employee:view_payroll'  %}">
                      <span class="bi bi-cash-coin nav-icon"></span>
                      <span class="nav-text">Payroll</span>
                  </a>
              </li>
              {% if reporting_take == True %}
              <li class="nav-item {% if url_name == 'leaves_lists' %}active{% endif %}">
                  <a class="nav-link" href="{% url 'employee:leaves_lists' emp_id %}">
                      <span class="bi bi-bookmark-x nav-icon"></span>
                      <span class="nav-text">Leave Approvals</span></a>
              </li>
              {% endif %}
              {% if reporting_take == True %}
              <li class="nav-item {% if url_name == 'resign_lists' %}active{% endif %}">
                  <a class="nav-link" href="{% url 'employee:resign_lists' emp_id %}">
                      <span class="bi bi-bookmark-x nav-icon"></span>
                      <span class="nav-text">Resignation Approvals</span></a>
              </li>
              {% endif %}
            </ul>
            {% endwith %}
          </nav>
        `;
      })
      .catch(error => console.error('Error loading content:', error));
  }

  // Add event listener to the switch button
  document.getElementById('switch-button').addEventListener('click', function() {
    // Call the switchPage function
    switchPage();
  });

  // Initial load of content
  switchPage(); // Load default content
from app import db

class Manager(db.Model):
    __tablename__ = 'Managers'
    id = db.Column('ManagerID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(50), nullable=False)
    email = db.Column('Email', db.String(120), nullable=False)
    password = db.Column('Password', db.String(120), nullable=False)
    department = db.Column('Department', db.String(100), nullable=True)

class Gate(db.Model):
    __tablename__ = 'Gates'
    id = db.Column('GateID', db.Integer, primary_key=True)
    gate_number = db.Column('GateNumber', db.String(50), nullable=False)
    location = db.Column('Location', db.String(100), nullable=False)

class Visitor(db.Model):
    __tablename__ = 'Visitors'@{
    ViewData["Title"] = "Manager Dashboard";
    Layout = "~/Views/Shared/_Layout.cshtml";
}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@ViewData["Title"]</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <link rel="stylesheet" href="~/css/manager_dashboard.css">
    <script>
        let selectedSuggestionIndex = -1;
        let activeFilters = { status: [], sort: [] };

        function toggleFilter(element) {
            const filterType = element.getAttribute('data-filter-type');
            const filterValue = element.getAttribute('data-value');

            if (filterType === 'status') {
                toggleFilterValue(activeFilters.status, filterValue);
            } else if (filterType === 'sort') {
                toggleFilterValue(activeFilters.sort, filterValue);
            }

            updateFiltersDisplay();
        }

        function toggleFilterValue(filterArray, filterValue) {
            const index = filterArray.indexOf(filterValue);
            if (index === -1) {
                filterArray.push(filterValue);
            } else {
                filterArray.splice(index, 1);
            }
        }

        function updateFiltersDisplay() {
            document.querySelectorAll('.dropdown-menu li').forEach(item => {
                const filterType = item.getAttribute('data-filter-type');
                const filterValue = item.getAttribute('data-value');
                if ((filterType === 'status' && activeFilters.status.includes(filterValue)) ||
                    (filterType === 'sort' && activeFilters.sort.includes(filterValue))) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
            applyFilters();
        }

        function applyFilters() {
            let queryParams = [];

            let searchValue = document.getElementById('search').value;
            if (searchValue) {
                queryParams.push(`search=${searchValue}`);
            }

            if (activeFilters.status.length > 0) {
                queryParams.push(`status=${activeFilters.status.join(',')}`);
            }
            if (activeFilters.sort.length > 0) {
                queryParams.push(`sort=${activeFilters.sort.join(',')}`);
            }

            let queryString = queryParams.join('&');
            let baseUrl = new URL(window.location.href);
            baseUrl.pathname = '@Url.Action("ManagerDashboard", "Home")';
            baseUrl.search = queryString;
            window.location.href = baseUrl.href;
        }

        function showSuggestions(query) {
            const suggestions = document.getElementById('suggestions');

            if (!/^\d*$/.test(query) || query.length === 0) {
                suggestions.innerHTML = '';
                suggestions.classList.remove('visible');
                return;
            }

            fetch(`/suggestions?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    suggestions.innerHTML = '';
                    if (data.length > 0) {
                        data.forEach((item, index) => {
                            let listItem = document.createElement('li');
                            listItem.textContent = item;
                            listItem.onclick = () => selectSuggestion(item);
                            listItem.setAttribute('data-index', index);
                            suggestions.appendChild(listItem);
                        });
                        suggestions.classList.add('visible');
                    } else {
                        suggestions.classList.remove('visible');
                    }
                })
                .catch(error => {
                    console.error('Error fetching suggestions:', error);
                });
        }

        function handleKeyDown(event) {
            const suggestions = document.getElementById('suggestions').getElementsByTagName('li');
            if (event.key === 'ArrowDown') {
                selectedSuggestionIndex = (selectedSuggestionIndex + 1) % suggestions.length;
                updateActiveSuggestion(suggestions);
            } else if (event.key === 'ArrowUp') {
                selectedSuggestionIndex = (selectedSuggestionIndex - 1 + suggestions.length) % suggestions.length;
                updateActiveSuggestion(suggestions);
            } else if (event.key === 'Enter') {
                event.preventDefault(); // Prevent form submission
                if (selectedSuggestionIndex > -1 && suggestions[selectedSuggestionIndex]) {
                    selectSuggestion(suggestions[selectedSuggestionIndex].textContent);
                }
            }
        }

        function showManagerDropdown(button) {
            if (!button) {
                console.error("Button element is undefined.");
                return;
            }

            // Find the parent container
            var parentContainer = button.closest('.details-row');
            if (!parentContainer) {
                console.error("Parent container is not found.");
                return;
            }

            // Find the existing manager name element and hide it
            var managerNameElement = parentContainer.querySelector('.manager-name');
            if (managerNameElement) {
                managerNameElement.style.display = 'none';
            } else {
                console.error("Manager name element is not found.");
            }

            // Find the dropdown for manager selection and show it
            var managerDropdownElement = parentContainer.querySelector('.manager-dropdown');
            if (managerDropdownElement) {
                managerDropdownElement.style.display = 'block';
            } else {
                console.error("Manager dropdown element is not found.");
            }

            // Show the confirm and cancel buttons
            var confirmButton = parentContainer.querySelector('.confirm-button');
            var cancelButton = parentContainer.querySelector('.cancel-button');
            if (confirmButton) {
                confirmButton.style.display = 'inline-block';
            }
            if (cancelButton) {
                cancelButton.style.display = 'inline-block';
            }
        }

        function hideManagerDropdown(button) {
            if (!button) {
                console.error("Button element is undefined.");
                return;
            }

            // Find the parent container
            var parentContainer = button.closest('.details-row');
            if (!parentContainer) {
                console.error("Parent container is not found.");
                return;
            }

            // Hide the dropdown for manager selection
            var managerDropdownElement = parentContainer.querySelector('.manager-dropdown');
            if (managerDropdownElement) {
                managerDropdownElement.style.display = 'none';
            } else {
                console.error("Manager dropdown element is not found.");
            }

            // Show the existing manager name element
            var managerNameElement = parentContainer.querySelector('.manager-name');
            if (managerNameElement) {
                managerNameElement.style.display = 'block';
            } else {
                console.error("Manager name element is not found.");
            }

            // Hide the confirm and cancel buttons
            var confirmButton = parentContainer.querySelector('.confirm-button');
            var cancelButton = parentContainer.querySelector('.cancel-button');
            if (confirmButton) {
                confirmButton.style.display = 'none';
            }
            if (cancelButton) {
                cancelButton.style.display = 'none';
            }
        }

        function assignNewManager(visitRequestID) {
            // Debugging: Print visitRequestID
            console.log("Visit Request ID:", visitRequestID);

            // Get the selected manager ID from the dropdown
            var newManagerID = document.getElementById('managerDropdown-' + visitRequestID).value;

            // Debugging: Print newManagerID
            console.log("New Manager ID:", newManagerID);

            // Send an AJAX request to the server to update the manager
            fetch(`/update_manager/${visitRequestID}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ new_manager_id: newManagerID })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Manager updated successfully.');
                        location.reload(); // Reload the page or update the UI as needed
                    } else {
                        alert('Error updating manager: ' + data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
        }

        function updateActiveSuggestion(suggestions) {
            Array.from(suggestions).forEach((suggestion, index) => {
                if (index === selectedSuggestionIndex) {
                    suggestion.classList.add('active');
                    suggestion.scrollIntoView({ block: 'nearest', inline: 'start' });
                } else {
                    suggestion.classList.remove('active');
                }
            });
        }

        function selectSuggestion(value) {
            document.getElementById('search').value = value;
            document.getElementById('suggestions').innerHTML = '';
            document.getElementById('suggestions').classList.remove('visible');
            selectedSuggestionIndex = -1;
            applyFilters();
        }

        function clearSearch() {
            document.getElementById('search').value = '';
            document.getElementById('suggestions').innerHTML = '';
            selectedSuggestionIndex = -1;
            applyFilters();
        }

        function toggleDetails(element) {
            const detailsRow = element.closest('tr').nextElementSibling;
            if (detailsRow && detailsRow.classList.contains('details-row')) {
                if (detailsRow.style.display === 'none' || detailsRow.style.display === '') {
                    detailsRow.style.display = 'table-row';
                } else {
                    detailsRow.style.display = 'none';
                }
            }
        }

        function updateVisitStatus(visitRequestID, status) {
            // Get the selected gate number from the dropdown
            const gateSelect = document.getElementById(`gateSelect-${visitRequestID}`);
            const gateID = gateSelect.value;

            // Ensure a gate is selected if the status is 'Approved'
            if (status === 'Approved' && !gateID) {
                alert('Please select a gate before approving the visit.');
                return;
            }

            fetch(`/update_visit_status/${visitRequestID}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: status, gate_id: gateID })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Status updated successfully');
                        location.reload(); // Reload the page or update the UI as needed
                    } else {
                        alert('Error updating status: ' + data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
        }

        document.addEventListener('DOMContentLoaded', function () {
            document.getElementById('search').addEventListener('keydown', handleKeyDown);
            document.querySelectorAll('.dropdown-menu li').forEach(item => {
                item.addEventListener('click', function (event) {
                    event.stopPropagation();
                    toggleFilter(item);
                });
            });

            window.addEventListener('click', function (event) {
                const dropdown = document.querySelector('.dropdown');
                if (!dropdown.contains(event.target)) {
                    document.querySelector('.dropdown-menu').style.display = 'none';
                } else {
                    document.querySelector('.dropdown-menu').style.display = 'block';
                }
            });
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <img src="~/assets/cal.png" alt="Cameron Logo" class="logo">
            <hr class="sidebar-separator">
            <a href="@Url.Action("Index", "Home")" class="nav-link">
                <i class="fas fa-home"></i>
                HOME
            </a>
            <a href="javascript:history.back()" class="nav-link">
                <i class="fas fa-arrow-left"></i>
                BACK
            </a>
        </div>
        <div class="main-box">
            <div class="header">
                <h1>Manager Dashboard</h1>
                <div class="summary-sort">
                    <div class="summary">
                        <div class="summary-item">
                            <div class="summary-title">Total Forms</div>
                            <div class="summary-value">@Model.TotalForms</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-title">Pending</div>
                            <div class="summary-value">@Model.PendingForms</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-title">Approved</div>
                            <div class="summary-value">@Model.ApprovedForms</div>
                        </div>
                    </div>
                    <div class="search-sort">
                        <form id="search-form" method="GET" action="@Url.Action("ManagerDashboard", "Home")">
                            <div class="search-bar" style="position: relative;">
                                <input type="text" id="search" name="search" placeholder="Search..." oninput="showSuggestions(this.value)" autocomplete="off">
                                <button type="button" class="clear-button" onclick="clearSearch()" aria-label="Clear search">×</button>
                                <ul id="suggestions" class="suggestions-list"></ul>
                            </div>
                        </form>
                        <div class="dropdown">
                            <button type="button" class="dropdown-button">Filter</button>
                            <ul class="dropdown-menu">
                                <li data-filter-type="sort" data-value="newest"><a>Newest</a></li>
                                <li data-filter-type="sort" data-value="oldest"><a>Oldest</a></li>
                                <li data-filter-type="status" data-value="Pending"><a>Pending</a></li>
                                <li data-filter-type="status" data-value="Approved"><a>Approved</a></li>
                                <li data-filter-type="status" data-value="Rejected"><a>Rejected</a></li>
                                <li data-filter-type="status" data-value="Checked In"><a>Checked In</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <table class="table">
                <thead>
                    <tr>
                        <th>Visit Request ID</th>
                        <th>Status</th>
                        <th>The Number of Visitors</th>
                        <th>Form Submission Time</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach (var detail in Model.VisitDetails)
                    {
                        <tr class="summary-row" onclick="toggleDetails(this)">
                            <td>@detail.Visit.VisitRequestID</td>
                            <td>@detail.Visit.Status</td>
                            <td>@detail.Visitors.Count</td>
                            <td>
                                @if (detail.Visit.SubmissionTime != null)
                                {
                                    @detail.Visit.SubmissionTime.Value.ToString("yyyy-MM-dd HH:mm")
                                }
                                else
                                {
                                    <text>N/A</text>
                                }
                            </td>
                            <td>
                                <span class="show-details">Show Details <i class="fas fa-chevron-down"></i></span>
                            </td>
                        </tr>
                        <tr class="details-row" style="display:none;">
                            <td colspan="5">
                                <div class="details">
                                    <h3>Manager Details:</h3>
                                    <ul>
                                        <li class="manager-name">Name: @detail.ManagerName</li>
                                        <li>Department: @detail.ManagerDepartment</li>
                                        <li>Edit: <a href="#" onclick="showManagerDropdown(this)">Edit</a></li>
                                        @if (detail.Visit.LastEdited != null)
                                        {
                                            <li>Last edited: @detail.Visit.LastEdited.Value.ToString("hh:mm tt")</li>
                                        }
                                        <li class="manager-dropdown" style="display:none;">
                                            <select id="managerDropdown-@detail.Visit.VisitRequestID">
                                                @foreach (var manager in Model.Managers)
                                                {
                                                    @if (manager.Id != detail.Visit.ManagerID)
                                                    {
                                                        <option value="@manager.Id">@manager.Name</option>
                                                    }
                                                }
                                            </select>
                                            <button class="confirm-button" style="display:none;" onclick="assignNewManager(@detail.Visit.VisitRequestID)">Confirm</button>
                                            <button class="cancel-button" style="display:none;" onclick="hideManagerDropdown(this)">Cancel</button>
                                        </li>
                                    </ul>

                                    <h3>Gate Security Details:</h3>
                                    <ul>
                                        <li>Name: @detail.GateSecurityName</li>
                                    </ul>

                                    <h3>Visitors:</h3>
                                    <ul>
                                        @foreach (var visitor in detail.Visitors)
                                        {
                                            <li>@visitor.FirstName @visitor.LastName (@visitor.Email) - ID/iqama: @visitor.IDNumber</li>
                                        }
                                    </ul>

                                    <h3>Location and Gate:</h3>
                                    <ul>
                                        <li>
                                            <label for="gateSelect-@detail.Visit.VisitRequestID">Assign Gate:</label>
                                            <select id="gateSelect-@detail.Visit.VisitRequestID" @(detail.Visit.Status != "Pending" ? "disabled" : "")>
                                                <option value="">Select a gate</option>
                                                @foreach (var gate in Model.Gates)
                                                {
                                                    <option value="@gate.Id" @(detail.Visit.GateID == gate.Id ? "selected" : "")>@gate.GateNumber</option>
                                                }
                                            </select>
                                        </li>
                                    </ul>

                                    <h3>Visit Times:</h3>
                                    <ul>
                                        @foreach (var time in detail.VisitTimes)
                                        {
                                            <li>@time.VisitDate from @time.StartTime to @time.EndTime</li>
                                        }
                                    </ul>

                                    @if (detail.Visit.CheckedInTime != null)
                                    {
                                        <h3>Checked In Time:</h3>
                                        <ul>
                                            <li>@detail.Visit.CheckedInTime.Value.ToString("yyyy-MM-dd HH:mm:ss")</li>
                                        </ul>
                                    }

                                    <div class="button-group">
                                        @if (detail.Visit.Status == "Pending")
                                        {
                                            <button class="approve-button" onclick="updateVisitStatus(@detail.Visit.VisitRequestID, 'Approved')">Approve</button>
                                            <button class="reject-button" onclick="updateVisitStatus(@detail.Visit.VisitRequestID, 'Rejected')">Reject</button>
                                        }
                                    </div>
                                </div>
                            </td>
                        </tr>
                    }
                </tbody>
            </table>

            <div class="pagination">
                @foreach (var p in Model.PaginatedVisits.GetPages())
                {
                    if (p.HasValue)
                    {
                        if (p == Model.PaginatedVisits.PageNumber)
                        {
                            <strong class="active">@p.Value</strong>
                        }
                        else
                        {
                            <a href="@Url.Action("ManagerDashboard", "Home", new { sort = Context.Request.Query["sort"], page = p })">@p.Value</a>

                        }
                    }
                    else
                    {
                        <span>...</span>
                    }
                }
            </div>
        </div>
    </div>
</body>
</html>

    id = db.Column('VisitorID', db.Integer, primary_key=True)
    first_name = db.Column('FirstName', db.String(50), nullable=False)
    last_name = db.Column('LastName', db.String(50), nullable=False)
    phone_number = db.Column('PhoneNumber', db.String(20), nullable=False)
    id_number = db.Column('IDNumber', db.String(50), nullable=False)
    email = db.Column('Email', db.String(120), nullable=False)
    visit_request_id = db.Column('VisitRequestID', db.Integer, db.ForeignKey('VisitRequests.VisitRequestID'), nullable=False)
    visit_request = db.relationship('VisitRequest', back_populates='visitors')

class VisitRequest(db.Model):
    __tablename__ = 'VisitRequests'
    id = db.Column('VisitRequestID', db.Integer, primary_key=True)
    manager_id = db.Column('ManagerID', db.Integer, db.ForeignKey('Managers.ManagerID'), nullable=False)
    gate_id = db.Column('GateID', db.Integer, db.ForeignKey('Gates.GateID'), nullable=False)
    status = db.Column('Status', db.String(20), nullable=False, default='Pending')
    submission_time = db.Column('SubmissionTime', db.DateTime, default=db.func.current_timestamp())
    checked_in_time = db.Column('CheckedInTime', db.DateTime, nullable=True)

    manager = db.relationship('Manager', backref=db.backref('visit_requests', lazy=True))
    gate = db.relationship('Gate', backref=db.backref('visit_requests', lazy=True))
    visitors = db.relationship('Visitor', back_populates='visit_request')
    visit_times = db.relationship('VisitTime', backref='visit_request', lazy=True)

class VisitTime(db.Model):
    __tablename__ = 'VisitTimes'
    id = db.Column('VisitTimeID', db.Integer, primary_key=True)
    visit_request_id = db.Column('VisitRequestID', db.Integer, db.ForeignKey('VisitRequests.VisitRequestID'), nullable=False)
    visit_date = db.Column('VisitDate', db.Date, nullable=False)
    start_time = db.Column('StartTime', db.Time, nullable=False)
    end_time = db.Column('EndTime', db.Time, nullable=False)

class GateAccount(db.Model):
    __tablename__ = 'GateAccounts'
    id = db.Column('GateAccountID', db.Integer, primary_key=True)
    gate_id = db.Column('GateID', db.Integer, db.ForeignKey('Gates.GateID'), nullable=False)
    username = db.Column('Username', db.String(50), nullable=False)
    password = db.Column('Password', db.String(120), nullable=False)
    name = db.Column('Name', db.String(50), nullable=False)

    gate = db.relationship('Gate', backref=db.backref('gate_accounts', lazy=True))

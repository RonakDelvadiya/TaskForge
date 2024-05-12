## TaskForge : Field Service Management API

The Field Service Management API provides endpoints to manage field service tasks for **Service Managers** and **Workers**.

**Main Objective**

The primary goal of the TaskForge's digital transformation is to enable efficient management of field service tasks. These tasks originate from client complaints received via multiple channels, including phone calls, emails, and the public portal feature on the web portal.

Service Managers play a pivotal role in this process by creating field service tasks, assigning priority, severity levels, and deadlines based on the urgency and criticality of each issue. These tasks are then allocated to expert service workers based on their availability and skill sets.

Once assigned, workers can view and interact with their designated tasks, adding essential notes for collaboration and review by Service Managers. Upon completion, workers must select a predefined reason from a list to provide closure on the task.

A comprehensive dashboard is provided to Service Managers, enabling them to oversee the task lifecycle with critical metrics:
1. **Number of Created Tasks**: Filterable by assignee, deadline, and creation timespan.
2. **Number of Completed Tasks**: Filterable by completion reason and completion datetime.

This application is poised to revolutionize TaskForge's operational efficiency, enabling seamless collaboration between Service Managers and workers while ensuring optimal management of field service tasks in response to client needs.

### API Endpoints to perform required tasks.

For all of the APIs doc string added in code along with URL, request body and response. For specific condition, descritive comments is also added.

1. **Add/Update Field Service Task**
   - **URL:** `/task-management/task-manage-operation/`
   - **Method:** POST
   - **Description:** Allows Service Managers to add a new field service task. The same API can be used to update an existing task by providing its ID.

2. **List All Tasks (Service Managers and Workers)**
   - **URL:** `/task-management/task-manage-operation/`
   - **Method:** GET
   - **Description:** Allows Service Managers to view all field service tasks. Workers can see tasks assigned to them.
   - **Filters:**
     - `priority` (exact match)
     - `severity` (exact match)
     - `task_status` (exact match)
     - `completion_reason` (exact match)
     - `completion_date` (exact, greater than, less than match)
   - **Filter Example URL:** `/task-management/task-manage-operation/?task_status=pending&completion_date__gt=2014-05-10`
   - **Default Behavior:** Sort by priority, severity, and descending deadline.

3. **Update Task Status and Notes (for Workers)**
   - **URL:** `/task-management/task-update-for-worker/`
   - **Method:** PUT
   - **Description:** Allows Workers to update task status, notes, completion reason, and completion date for assigned tasks.

4. **KPIs for Dashboard (For Service Managers)**
   - **URL:** `/task-management/task-kpis/`
   - **Method:** GET
   - **Description:** Service Managers can view Key Performance Indicators (KPIs) of completed and created tasks.
   - **Filters for Created Tasks:**
     - `assignee`
     - `deadline` (less than or equal to)
     - Range of created date (`created_on_start_date`, `created_on_end_date`)
   - **Filters for Completed Tasks:**
     - `completion_reason` (exact match)
     - `completion_datetime` (less than or equal to)
   - **Filter Example URL:** `/task-management/task-kpis/?assignee=3&deadline=2014-05-10`

This README provides an overview of the available endpoints and their functionalities within the TaskForge APIs. Each endpoint specifies its URL, HTTP method, description, and supported filters for data retrieval and manipulation. Use these endpoints to efficiently manage and track field service tasks based on user roles and access permissions. Adjust filter parameters in the API calls to retrieve specific task data as needed.

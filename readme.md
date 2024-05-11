Field Service Management API
These API provides endpoints to manage field service tasks for Service Managers and Workers.

Endpoints

1. Add/Update Field Service Task
        URL: /task-management/task-manage-operation/
        Method: POST
        Description: Allows Service Managers to add a new field service task, same api will be used for update task if provides ID of existing task.

2. List All Tasks (Service Managers and Workers)
        URL: /task-management/task-manage-operation/
        Method: GET
        Description: Allows Service Managers(Can see all tasks) and Workers(Can see all tasks which assigned to him/her) to view all field service tasks. 
        Filter: priority(exact match), severity(exact match), task_status(exact match), completion_reason(exact match), completion_date(exact, gt, lt match)
        Filter Example URL: /task-management/task-manage-operation/?task_status=pending&completion_date__gt=2014-05-10
        Behaviour: Sort by priority, severity and descending by deadline.

3. Update Task Status and Notes (for Workers)
        URL: /task-management/task-update-for-worker/
        Method: PUT
        Description: Allows Workers to update only task status, note, completion reason, completion date for assigned tasks.

4. KPIs for dashboard(For Service Managers)
        URL: /task-management/task-kpis/
        Method: GET
        Description: Service Managers can see KPIs of completed and created Tasks.
        Filter: For Created tasks => assignee, deadline(less than or equal to), range of created date(created_on_start_date, created_on_end_date).
                For Completed tasks => completion_reason(exact match), completion_datetime(less than or equal to, for this )
        Filter Example URL: /task-management/task-kpis/?assignee=3&deadline=2014-05-10
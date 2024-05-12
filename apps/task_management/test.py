from rest_framework.test import *
from rest_framework import status
from django.urls import reverse
from task_management.models import *
from users.models import UserProfile
from task_management.views import *


class TaskManageCrudOperationTestCase(APITestCase):
    def setUp(self):
        self.manager_user = UserProfile.objects.create(username='manager', role='Service Manager')
        self.assignee_user = UserProfile.objects.create(username='assignee', role='Worker')
        self.admin = UserProfile.objects.create(username='other', role='Admin')
        self.view = TaskManageCrudOperation.as_view()
        self.factory = APIRequestFactory()
        self.url = reverse('task_manage_operation')


    def test_valid_task_creation_by_manager(self):
        data = {
            "title": "First Task",
            "task_status": "pending",
            "description": "Test description",
            "priority": 1,
            "severity": 3,
            "deadline": "2014-05-10",
            "complaints_received_via": "phone",
            "assignee": self.assignee_user.id  # Use ID instead of UserProfile instance
        }
        request = self.factory.post(self.url, data, format='json')
        force_authenticate(request, user=self.manager_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_valid_task_update_by_manager(self):
        # Create a TaskManage instance with a valid manager_id
        task = TaskManage.objects.create(
            title="Existing Task",
            task_status="pending",
            description="Existing description",
            priority=1,
            severity=3,
            deadline="2014-05-10",
            complaints_received_via="phone",
            assignee=self.assignee_user,
            manager=self.manager_user  # Set manager_id to the manager user
        )

        data = {
            "id": task.id,
            "title": "Updated Task",
            "task_status": "completed",
            "description": "Updated description",
            "priority": 2,
            "severity": 4,
            "deadline": "2014-05-15",
            "complaints_received_via": "email",
            "assignee": self.assignee_user.id,
            "manager": self.manager_user.id  # Provide manager_id based on the manager user
        }

        request = self.factory.post(self.url, data, format='json')
        force_authenticate(request, user=self.manager_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_unauthorized_task_creation_by_non_manager(self):
        data = {
            "title": "Unauthorized Task",
            "task_status": "pending",
            "description": "Test description",
            "priority": 1,
            "severity": 3,
            "deadline": "2014-05-10",
            "complaints_received_via": "phone",
            "assignee": self.assignee_user.id  # Use ID instead of UserProfile instance
        }
        request = self.factory.post(self.url, data, format='json')
        force_authenticate(request, user=self.assignee_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_invalid_task_creation_missing_fields(self):
        # Create a dictionary with only required fields (but missing 'title')
        data = {
            "task_status": "pending",
            "description": "Test description",
            "priority": 1,
            "severity": 3,
            "deadline": "2014-05-10",
            "complaints_received_via": "phone",
            "assignee": self.assignee_user.id  # Use ID instead of user instance
        }

        request = self.factory.post(self.url, data, format='json')
        force_authenticate(request, user=self.manager_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_invalid_task_update_by_non_manager(self):
        # Create a TaskManage instance
        task = TaskManage.objects.create(
            title="Existing Task",
            task_status="pending",
            description="Existing description",
            priority=1,
            severity=3,
            deadline="2014-05-10",
            complaints_received_via="phone",
            assignee=self.assignee_user,
            manager=self.manager_user  # Set manager_id to the manager user
        )

        data = {
            "id": task.id,
            "title": "Updated Task",
            "task_status": "completed",
            "description": "Updated description",
            "priority": 2,
            "severity": 4,
            "deadline": "2014-05-15",
            "complaints_received_via": "email",
            "assignee": self.assignee_user.id,
            "manager": self.manager_user.id  # Provide manager_id based on the manager user
        }
        request = self.factory.post(self.url, data, format='json')
        force_authenticate(request, user=self.admin)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        
class WorkerTaskUpdateTestCase(APITestCase):

    def setUp(self):
        # Create a manager user for assigning tasks
        self.manager_user = UserProfile.objects.create(username='manager', role='Service Manager')

        # Create a worker user for updating tasks
        self.worker_user = UserProfile.objects.create(username='worker', role='Worker')

        self.admin = UserProfile.objects.create(username='other', role='Admin')
        
        # Create a task assigned by the manager user
        self.task = TaskManage.objects.create(
            title="Test Task",
            task_status="pending",
            description="Test description",
            priority=1,
            severity=3,
            deadline="2014-05-10",
            complaints_received_via="phone",
            assignee=self.worker_user,  # Assign the task to the worker user
            manager=self.manager_user  # Set the manager for the task
        )

        self.url = reverse('task_update_for_worker')

        self.view = WorkerTaskUpdate.as_view()

        self.factory = APIRequestFactory()


    def test_valid_task_update_by_worker(self):
        data = {
            "id": self.task.id,
            "task_status": "in_progress",
            "assignee_note": "Test Note in progress",
            "completion_reason": "technical_limitation"
        }

        request = self.factory.put(self.url, data, format='json')
        force_authenticate(request, user=self.worker_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_status'], 'in_progress')
        self.assertEqual(response.data['assignee_note'], 'Test Note in progress')
        self.assertEqual(response.data['completion_reason'], 'technical_limitation')


    def test_task_update_without_id(self):
        data = {
            "task_status": "in_progress",
            "assignee_note": "Test Note in progress",
            "completion_reason": "technical_limitation"
        }
        request = self.factory.put(self.url, data, format='json')
        force_authenticate(request, user=self.worker_user)
        response = self.view(request)
        # import pdb; pdb.set_trace();
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('id is required', response.data['error'])


    def test_unauthorized_task_update_by_admin(self):
        data = {
            "id": self.task.id,
            "task_status": "in_progress",
            "assignee_note": "Test Note in progress",
            "completion_reason": "technical_limitation"
        }
        request = self.factory.put(self.url, data, format='json')
        
        # Make an authenticated request to the view...
        force_authenticate(request, user=self.manager_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Only Workers can update tasks', response.data['error'])


class TaskKPIsTestCase(APITestCase):
    def setUp(self):
        # Create a manager user for assigning tasks
        self.manager_user = UserProfile.objects.create(username='manager', role='Service Manager')

        # Create a worker user for updating tasks
        self.worker_user = UserProfile.objects.create(username='worker', role='Worker')
        
        # Create example tasks for testing
        self.url = reverse('task_kpis')  # Assuming 'task_kpis' is the name of the endpoint

        self.view = TaskKPIs.as_view()

        self.factory = APIRequestFactory()

        TaskManage.objects.create(
            title="Task 1",
            task_status="pending",
            assignee=self.worker_user,
            manager=self.manager_user,
            deadline="2014-05-15"
        )

        TaskManage.objects.create(
            title="Task 2",
            task_status="completed",
            assignee=self.worker_user,
            manager=self.manager_user,
            deadline="2014-05-20"
        )


    def test_task_kpis_endpoint(self):
        """
        Test the /task-management/task-kpis/ endpoint to ensure correct KPIs response.
        """
        request = self.factory.get(self.url)
        
        # Make an authenticated request to the view...
        force_authenticate(request, user=self.manager_user)
        
        response = self.view(request)
        self.assertEqual(response.status_code, 200)


    def test_get_created_tasks_count(self):
        """
        Test the method get_created_tasks_count to ensure correct count of created tasks.
        """
        request = self.factory.get(self.url)
        
        # Make an authenticated request to the view...
        force_authenticate(request, user=self.manager_user)
        
        response = self.view(request)
        self.assertEqual(response.data['created_tasks_count'], 2)  # Expected created tasks count


    def test_get_completed_tasks_count(self):
        """
        Test the method get_completed_tasks_count to ensure correct count of completed tasks.
        """
        request = self.factory.get(self.url)
        
        # Make an authenticated request to the view...
        force_authenticate(request, user=self.manager_user)
        
        response = self.view(request)
        
        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Assert that the 'completed_tasks_count' in the response data is as expected (1 completed task)
        self.assertEqual(response.data['completed_tasks_count'], 1)
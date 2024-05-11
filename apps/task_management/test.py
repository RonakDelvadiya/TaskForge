from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import TaskManage
from users.models import UserProfile

class TaskManageCrudOperationTestCase(APITestCase):
    def setUp(self):
        self.manager_user = UserProfile.objects.create(username='manager', role='Service Manager')
        self.assignee_user = UserProfile.objects.create(username='assignee', role='Worker')
        self.admin = UserProfile.objects.create(username='other', role='Admin')

    def test_valid_task_creation_by_manager(self):
        url = reverse('task_manage_operation')  # Update the reverse call
        self.client.force_authenticate(user=self.manager_user)

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

        response = self.client.post(url, data, format='json')
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

        url = reverse('task_manage_operation')  # Update the reverse call
        self.client.force_authenticate(user=self.manager_user)

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

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_task_creation_by_non_manager(self):
        url = reverse('task_manage_operation')  # Update the reverse call
        self.client.force_authenticate(user=self.admin)

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

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_task_creation_missing_fields(self):
        url = reverse('task_manage_operation')  # Update the reverse call
        self.client.force_authenticate(user=self.manager_user)

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

        response = self.client.post(url, data, format='json')
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

        url = reverse('task_manage_operation')  # Update the reverse call
        self.client.force_authenticate(user=self.admin)

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

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class WorkerTaskUpdateTestCase(APITestCase):

    def setUp(self):
        # Create a manager user for assigning tasks
        self.manager_user = UserProfile.objects.create(username='manager', role='Manager')

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

    def test_valid_task_update_by_worker(self):
        url = reverse('task_update_for_worker')  # Update with the correct URL name
        self.client.force_authenticate(user=self.worker_user)

        data = {
            "id": self.task.id,
            "task_status": "in_progress",
            "assignee_note": "Test Note in progress",
            "completion_reason": "technical_limitation"
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_status'], 'in_progress')
        self.assertEqual(response.data['assignee_note'], 'Test Note in progress')
        self.assertEqual(response.data['completion_reason'], 'technical_limitation')

    def test_task_update_without_id(self):
        url = reverse('task_update_for_worker')  # Update with the correct URL name
        self.client.force_authenticate(user=self.worker_user)

        data = {
            "task_status": "in_progress",
            "assignee_note": "Test Note in progress",
            "completion_reason": "technical_limitation"
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('id is required', response.data['error'])

    def test_unauthorized_task_update_by_admin(self):
        url = reverse('task_update_for_worker')  # Update with the correct URL name
        self.client.force_authenticate(user=self.admin)

        data = {
            "id": self.task.id,
            "task_status": "in_progress",
            "assignee_note": "Test Note in progress",
            "completion_reason": "technical_limitation"
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Only Workers can update tasks', response.data['error'])


class TaskKPIsTestCase(APITestCase):
    def setUp(self):
        # Create a manager user for assigning tasks
        self.manager_user = UserProfile.objects.create(username='manager', role='Manager')

        # Create a worker user for updating tasks
        self.worker_user = UserProfile.objects.create(username='worker', role='Worker')
        
        # Create example tasks for testing
        self.url = reverse('task_kpis')  # Assuming 'task_kpis' is the name of the endpoint

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
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_created_tasks_count(self):
        """
        Test the method get_created_tasks_count to ensure correct count of created tasks.
        """
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['created_tasks_count'], 2)  # Expected created tasks count

    def test_get_completed_tasks_count(self):
        """
        Test the method get_completed_tasks_count to ensure correct count of completed tasks.
        """
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['completed_tasks_count'], 1)  # Expected completed tasks count

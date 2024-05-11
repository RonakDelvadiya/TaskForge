from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.throttling import UserRateThrottle
from django.views.decorators.cache import cache_page  # Import cache_page decorator
from django.utils.decorators import method_decorator
import logging

from .models import TaskManage
from .serializers import AddUpdateTaskManageSerializer, ListTaskManageSerializer, UpdateTaskManageForWorkerSerializer


class TaskManageCrudOperation(generics.ListAPIView):
    """
    API to get, add, update tasks.
    Methods: GET, POST
    URL : http://127.0.0.1:8000/task-management/task-manage-operation/
    """
    authentication_classes = [SessionAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    throttle_classes = [UserRateThrottle]
    serializer_class = ListTaskManageSerializer
    search_fields = ("title","description")
    filterset_fields = {    
        'priority': ['exact'],
        'severity': ['exact'],
        'task_status': ['exact'],
        'completion_reason': ['exact'],
        'completion_date': ['exact', 'gt', 'lt'],  # Include 'gt' (greater than) and 'lt' (less than) filters
    }

    def get_queryset(self):
        if self.request.user.role == "Service Manager" or self.request.user.is_superuser :
            return TaskManage.objects.filter(is_active=True)
        else:
            return TaskManage.objects.filter(is_active=True, assignee=self.request.user)

    
    """
    Request Body : {
        "title": "First Task",
        "task_status": "pending",
        "description": "Test description",
        "priority": 1,
        "severity": 3,
        "deadline": "2014-05-10",
        "complaints_received_via": "phone",
        "assignee" : 3
    }
    """
    def post(self, request):
        try:
            if request.user.role == "Service Manager" or self.request.user.is_superuser :
                data = request.data
                data["manager"] = self.request.user.id
                if "id" in data :
                    task = TaskManage.objects.get(id=data["id"])
                    serializer = AddUpdateTaskManageSerializer(task, data=data)
                    if serializer.is_valid():
                        serializer.save(manager=request.user)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializer = AddUpdateTaskManageSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save(manager=request.user)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Only Service Managers can create or update whole tasks.'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WorkerTaskUpdate(APIView):
    """
    API to update task.
    Methods: PUT
    URL : http://127.0.0.1:8000/task-management/task-update-for-worker/
    """
    authentication_classes = [SessionAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    throttle_classes = [UserRateThrottle]
    api_view = ['PUT']


    """
    Request Body = {
        "id" : 3,
        "task_status": "in_progress",
        "assignee_note" : "Test Note in progress", 
        "completion_reason" : "technical_limitation",
        "completion_date" : "2014-09-09"
    }

    Response = {
                    "assignee_note": "Test Note in progress test 2",
                    "task_status": "in_progress",
                    "completion_reason": "technical_limitation",
                    "completion_date" : "2014-09-09"
                }
    """
    def put(self, request):
        try:
            if request.user.role == "Worker" or self.request.user.is_superuser:
                data = request.data
                task_id = data.get("id")
                if not task_id :
                    return Response({'error': 'id is required to update a task.'}, status=status.HTTP_400_BAD_REQUEST)
                
                task = TaskManage.objects.filter(id=task_id, assignee=request.user)
                if task : 
                    if data.get('task_status') == 'completed' and not data.get('completion_reason'):
                        return Response({'error': 'Completion reason is required to update as a completed tasks.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    serializer = UpdateTaskManageForWorkerSerializer(task.first(), data=data)
                    if serializer.is_valid():
                        # import pdb; pdb.set_trace();
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Task not found or this task is not assigned to you.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Only Workers can update tasks.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TaskKPIs(APIView):
    """
    API to get KPIs of tasks.
    Methods: GET
    URL : http://127.0.0.1:8000/task-management/task-kpis/
    Response : {
                    "created_tasks_count": 0,
                    "completed_tasks_count": 0
                }
    """
    authentication_classes = [SessionAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    throttle_classes = [UserRateThrottle]
    api_view = ['GET']

    def get_created_tasks_count(self):
        """
        Calculate the number of created tasks based on filters.
        """
        try:
            queryset = TaskManage.objects.filter(is_active=True)

            # Apply filters based on query parameters
            assignee = self.request.query_params.get('assignee')
            if assignee:
                queryset = queryset.filter(assignee_id=assignee)

            deadline = self.request.query_params.get('deadline')
            if deadline:
                queryset = queryset.filter(deadline__lte=deadline)

            created_on_start_date = self.request.query_params.get('created_on_start_date')
            created_on_end_date = self.request.query_params.get('created_on_end_date')
            
            if created_on_start_date and created_on_end_date :
                queryset.filter(created_on__range=(created_on_start_date, created_on_end_date))

            created_tasks_count = queryset.count()
            return created_tasks_count

        except Exception as e:
            raise e  # Raise exception to be caught by the parent try-except block


    def get_completed_tasks_count(self):
        """
        Calculate the number of completed tasks based on filters.
        """
        try:
            queryset = TaskManage.objects.filter(task_status='completed')

            # Apply filters based on query parameters
            completion_reason = self.request.query_params.get('completion_reason')
            if completion_reason:
                queryset = queryset.filter(completion_reason=completion_reason)

            # We can use range like creation timespan
            completion_datetime = self.request.query_params.get('completion_datetime')
            if completion_datetime:
                queryset = queryset.filter(completion_datetime__lte=completion_datetime)

            completed_tasks_count = queryset.count()
            return completed_tasks_count

        except Exception as e:
            raise e  # Raise exception to be caught by the parent try-except block


    @method_decorator(cache_page(120)) # Cache the response for 120 seconds
    def get(self, request):
        try:
            # Default response dictionary for KPIs
            kpi_data = {}

            # Number of created tasks (filtered by assignee, deadline, creation timespan)
            created_tasks_count = self.get_created_tasks_count()
            kpi_data['created_tasks_count'] = created_tasks_count

            # Number of completed tasks (filtered by complete reason, completion datetime)
            completed_tasks_count = self.get_completed_tasks_count()
            kpi_data['completed_tasks_count'] = completed_tasks_count
            return Response(kpi_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Staff
from .serializers import StaffSerializer


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get staff by user_id."""
        try:
            staff = Staff.objects.get(user_id=user_id)
            serializer = self.get_serializer(staff)
            return Response(serializer.data)
        except Staff.DoesNotExist:
            return Response(
                {'detail': 'Staff not found for this user_id.'},
                status=status.HTTP_404_NOT_FOUND
            )

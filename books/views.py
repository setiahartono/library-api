from django.http import JsonResponse
from rest_framework import permissions, viewsets
from rest_framework.views import APIView


# Create your views here.
from books.models import Book, Loan, LoanDetail
from books.permissions import LibrarianPermission
from books.serializers import BookSerializer, LoanDetailSerializer, LoanSerializer, ExtensionSerializer


class BookViewsets(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


class LoanedBookViewSets(viewsets.ModelViewSet):
    queryset = LoanDetail.objects.all()
    serializer_class = LoanDetailSerializer
    permission_classes_by_action = {
        'create': [LibrarianPermission]
    }

    def get_permissions(self):
        # Return the appropriate permission classes based on action
        return [permission() for permission in self.permission_classes_by_action.get(self.action, [])]

    def get_queryset(self):
        qs = super().get_queryset()
        try:
            if self.request.user.user_role.role == "STUDENT":
                qs = LoanDetail.objects.filter(
                    loan__loaner_id=self.request.user.id,
                    is_returned=False
                )
        except AttributeError:
            qs = []
        return qs

    def create(self, request, *args, **kwargs):
        self.serializer_class = LoanSerializer
        data = request.data
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
        else:
            return JsonResponse(serializer.errors, status=400)

        return JsonResponse({"message": "Loan is successful"}, status=201)


class ExtensionViewSets(viewsets.ModelViewSet):
    queryset = LoanDetail.objects.all()
    serializer_class = ExtensionSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.extension_requested_at is not None:
            return JsonResponse({"message": f"Extension failed - Book '{instance.book.title}' has been extended before"}, status=400)
        if instance.is_returned:
            return JsonResponse({"message": f"Extension failed - Book '{instance.book.title}' has been returned"}, status=400)

        serializer = self.get_serializer(instance, data={})

        if serializer.is_valid():
            serializer.save()
        else:
            return JsonResponse(serializer.errors, status=400)
        return super().update(request, *args, **kwargs)


class LoanHistoryViewsets(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.user_role.role == 'STUDENT':
            Loan.objects.filter(loaner=self.request.user)
        return qs


class ReturnsViews(APIView):
    queryset = LoanDetail.objects.all()
    permission_classes = [LibrarianPermission]

    def post(self, request, *args, **kwargs):
        ids = []
        try:
            data = request.data['loan_detail_ids']
        except (IndexError, TypeError, KeyError):
            return JsonResponse({"message": "Invalid JSON Format"}, status=400, safe=False)

        for loan_detail_id in data:
            ids.append(loan_detail_id)

        instances = LoanDetail.objects.filter(id__in=ids, is_returned=False)
        for instance in instances:
            instance.is_returned = True
            instance.save()
        serializer = LoanDetailSerializer(instances, many=True)

        return JsonResponse(
            {
                "message": "Valid loaned books returned successfully",
                "details": serializer.data
            }
        )

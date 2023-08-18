from django.urls import path

from books import views

urlpatterns = [
    path(r'books', views.BookViewsets.as_view({'get': 'list'})),
    path(r'loans', views.LoanedBookViewSets.as_view(
        {'get': 'list', 'post': 'create'})),
    path(r'extensions/<int:pk>',
         views.ExtensionViewSets.as_view({'put': 'update'})),
    path(r'histories',
         views.LoanHistoryViewsets.as_view({'get': 'list'})),
    path(r'returns', views.ReturnsViews.as_view()),
]

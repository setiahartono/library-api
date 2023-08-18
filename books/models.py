from django.db import models

# Create your models here.
from datetime import timedelta, date
from django.contrib.auth.models import User
from django.db import models

USER_ROLES = (
    ('STUDENT', 'Student'),
    ('LIBRARIAN', 'Librarian')
)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserRole(models.Model):
    """
    User Profile model to set user detail and role
    """
    user = models.OneToOneField(
        User, related_name='user_role', on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=USER_ROLES)


class Book(BaseModel):
    """
    Book model. Representing a book data
    """
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    author = models.CharField(max_length=200, db_index=True)
    stock = models.PositiveIntegerField(null=False, blank=False)

    @property
    def available_stock(self):
        return self.stock - LoanDetail.objects.filter(is_returned=False, book=self).count()

    @property
    def earliest_return_date(self):
        earliest_return_date = "-"
        if self.available_stock < 1:
            ld_instance = LoanDetail.objects.filter(is_returned=False, book=self).order_by(
                'expected_return_date'
            ).first()
            if ld_instance is not None:
                earliest_return_date = ld_instance.expected_return_date
        return earliest_return_date

    def __str__(self):
        return f"{self.title} - {self.author}"


class Loan(BaseModel):
    """
    Loan model. Representing a loan.
    """
    loaner = models.ForeignKey(User, on_delete=models.SET("USER REVOKED"))

    def __str__(self):
        return f"Loaner: {self.loaner} - Date: {self.created_at}"

    @property
    def owner(self):
        return self.loaner


class LoanDetail(BaseModel):
    """
    Loan detail containing each books borrowed
    """
    loan = models.ForeignKey(
        Loan, related_name='loan_details', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.SET("BOOK DELETED"))
    is_returned = models.BooleanField(default=False, null=False)
    extension_requested_at = models.DateField(
        default=None, null=True, blank=True
    )
    expected_return_date = models.DateField(
        default=date.today() + timedelta(days=30), null=False, blank=True
    )

    @property
    def owner(self):
        return self.loan.loaner

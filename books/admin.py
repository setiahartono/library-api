from django.contrib import admin
from django.contrib.auth import models as auth_models, admin as useradmin
# Register your models here.
from books.models import Book, Loan, LoanDetail, UserRole


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = [
        "title",
        "author",
        "available_stock",
        "created_at",
        "updated_at"
    ]


class LoanDetailInline(admin.TabularInline):
    model = LoanDetail


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    inlines = [LoanDetailInline]


class UserRoleInline(admin.StackedInline):
    model = UserRole


class UserAdminWithRole(useradmin.UserAdmin):
    inlines = [UserRoleInline]


admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, UserAdminWithRole)

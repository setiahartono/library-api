from datetime import date, timedelta

from rest_framework import serializers


from books.models import Book, Loan, LoanDetail


class BookSerializer(serializers.ModelSerializer):
    earliest_return_date = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'title', 'author', 'available_stock', 'description',
            'earliest_return_date'
        )

    def get_earliest_return_date(self, obj):
        return obj.earliest_return_date


class LoanDetailSerializer(serializers.ModelSerializer):
    book_info = serializers.SerializerMethodField()
    loan_detail_id = serializers.SerializerMethodField()

    class Meta:
        model = LoanDetail
        fields = (
            'loan_detail_id',
            'book_info',
            'book',
            'is_returned',
            'extension_requested_at',
            'expected_return_date'
        )

    def validate(self, data):
        book = data['book']
        if book.available_stock < 1:
            raise serializers.ValidationError("No more copies available")
        return super().validate(data)

    def get_book_info(self, obj):
        return f"{obj.book.title} by {obj.book.author}"

    def get_loan_detail_id(self, obj):
        return obj.id


class LoanSerializer(serializers.ModelSerializer):
    loan_details = LoanDetailSerializer(many=True)
    loan_id = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ('loaner', 'loan_id', 'loan_details')

    def get_loan_id(self, obj):
        return obj.id

    def validate(self, data):
        loan_data = data['loan_details']
        if len(loan_data) > 10:
            raise serializers.ValidationError(
                "Only 10 books can be borrowed at one time")
        return super().validate(data)

    def create(self, validated_data):
        loan_data = self.initial_data['loan_details']
        loan_instance = Loan.objects.create(loaner=validated_data['loaner'])

        for item in loan_data:
            LoanDetail.objects.create(loan=loan_instance, book_id=item['book'])

        return loan_instance


class ExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanDetail
        fields = (
            'extension_requested_at',
            'is_returned',
            'expected_return_date'
        )

    def validate(self, attrs):
        if self.instance is not None:
            if date.today() > self.instance.expected_return_date:
                raise serializers.ValidationError(
                    "Extension period has passed.")
        return super().validate(attrs)

    def update(self, instance, validated_data):
        instance.extension_requested_at = date.today()
        instance.expected_return_date = instance.extension_requested_at + \
            timedelta(days=30)
        instance.save()

        return instance

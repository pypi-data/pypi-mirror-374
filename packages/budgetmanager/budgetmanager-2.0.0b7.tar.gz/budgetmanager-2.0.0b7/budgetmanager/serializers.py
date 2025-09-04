from rest_framework.serializers import (
    HiddenField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    CurrentUserDefault,
)

from . import models


class UserSerializer(ModelSerializer):
    class Meta:
        model = models.Budget.get_user_model()
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
        )


class BaseSerializer(ModelSerializer):
    modified_by = PrimaryKeyRelatedField(read_only=True)
    modified_by_hidden = HiddenField(
        default=CurrentUserDefault(),
        source='modified_by'
    )


class BudgetSerializer(BaseSerializer):
    user = PrimaryKeyRelatedField(default=CurrentUserDefault(), read_only=True)

    class Meta:
        model = models.Budget
        fields = (
            'id',
            'name',
            'description',
            'active',
            'user',
            'last_modified',
            'modified_by',
            'modified_by_hidden',
        )


class BudgetListSerializer(BaseSerializer):
    class Meta:
        model = models.Budget
        fields = (
            'id',
            'name',
            'active',
            'user',
        )


class BudgetShareSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True)
    budget = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.BudgetShare
        fields = (
            'id',
            'budget',
            'user',
            'can_edit',
            'added',
            'added_by',
        )


class PayeeSerializer(BaseSerializer):
    class Meta:
        model = models.Payee
        fields = (
            'id',
            'name',
            'description',
            'budget',
            'last_modified',
            'modified_by',
            'modified_by_hidden',
        )


class PayeeListSerializer(BaseSerializer):
    class Meta:
        model = models.Payee
        fields = (
            'id',
            'name',
            'budget',
        )


class PaymentSerializer(BaseSerializer):
    class Meta:
        model = models.Payment
        fields = (
            'id',
            'notes',
            'payee',
            'amount',
            'date',
            'pending',
            'last_modified',
            'modified_by',
            'modified_by_hidden',
        )


class PaymentListSerializer(BaseSerializer):
    class Meta:
        model = models.Payment
        fields = (
            'id',
            'payee',
            'amount',
            'date',
        )


class ShareCodeSerializer(ModelSerializer):
    added_by = PrimaryKeyRelatedField(read_only=True)
    added_by_hidden = HiddenField(
        default=CurrentUserDefault(),
        source='added_by'
    )

    class Meta:
        model = models.ShareCode
        fields = (
            'id',
            'budget',
            'can_edit',
            'added_by',
            'added_by_hidden',
            'expiry',
        )

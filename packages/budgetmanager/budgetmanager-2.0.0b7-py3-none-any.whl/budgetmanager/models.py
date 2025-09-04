'''
Model classes
'''
# pylint:disable=no-member
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


def _get_total_amount(queryset) -> Decimal:
    return queryset.filter(pending=False).aggregate(
        models.Sum('amount', default=0)
    )['amount__sum']


def _get_sharecode_expiry():
    return timezone.now() + timedelta(days=10)


class BaseModel(models.Model):
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    class Meta:
        abstract = True


class Budget(BaseModel):
    '''
    Model for a budget
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    shared_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='BudgetShare',
        through_fields=('budget', 'user'),
        related_name='shared_budgets',
        blank=True,
    )
    last_used = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    @transaction.atomic
    def add_from_csv(self, text: str):
        '''
        Add payees and payments to this budget from a CSV formatted string
        '''
        rows = text.strip().split('\n')
        for line in rows:
            record = line.split(',')
            payee = Payee.objects.get_or_create(
                name=record[0],
                budget=self
            )[0]
            payment = Payment(
                payee=payee,
                amount=record[1],
                date=datetime.strptime(record[2], '%d/%m/%Y'),
            )
            if len(record) >= 4:
                payment.notes = record[3]
            if len(record) >= 5:
                payment.pending = record[4] != ''
            payment.save()
        self.last_used = datetime.now()

    @property
    def total(self):
        '''The total amount of the Payments of this Budget'''
        return _get_total_amount(Payment.objects.filter(payee__budget=self))

    @classmethod
    def get_user_model(cls):
        return cls._meta.get_field('user').related_model

    def has_access(self, user, editable: bool, requires_owner: bool = False):
        '''
        Check if user has access to this Budget
        editable: False for read access, True for write access
        '''
        res = (
            self.user == user or
            not requires_owner and self.shared_users.contains(user) and (
                (editable and self.budgetshare_set.get(
                    user=user).can_edit) or not editable
            )
        )
        return res


class BudgetShare(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
    added = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )

    def clean(self):
        if self.user == self.budget.user:
            raise ValidationError('Budget owner cannot be a shared user')

    @transaction.atomic
    def transfer_budget(self):
        budget = self.budget
        old_owner = budget.user
        budget.user = self.user
        self.delete()
        budget.save()
        BudgetShare.objects.create(
            user=old_owner, budget=budget, can_edit=True)

    def __str__(self):
        return f"{self.user} {'edit' if self.can_edit else 'access'} {self.budget.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('budget', 'user'), name='One budget membership per user per budget'),
        ]


class Payee(BaseModel):
    '''
    Model for a payee
    '''
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    last_used = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.budget.name})'

    @property
    def total(self):
        '''
        The total amount of the Payments of this Payee
        '''
        return _get_total_amount(self.payment_set)

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.budget.save()


class Payment(BaseModel):
    '''
    Model for a payment
    Requires a payee and a budget
    Has an amount and date
    '''
    payee = models.ForeignKey(
        Payee,
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(decimal_places=2, max_digits=7)
    date = models.DateField()
    pending = models.BooleanField(
        default=False, verbose_name='Exclude from total')
    notes = models.TextField(null=True, blank=True)

    @classmethod
    def get_total(cls, user):
        '''Get the total amount of the user's Payments'''
        return _get_total_amount(cls.objects.filter(
            models.Q(payee__budget__user=user) |
            models.Q(payee__budget_id__in=user.budgetshare_set.values('budget_id'))
        ))

    def __str__(self):
        if self.amount.is_signed():
            return f'{self.payee.name}: {abs(self.amount):.2f} from {self.payee.budget.name}'
        return f'{self.payee.name}: {self.amount:.2f} to {self.payee.budget.name}'

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.payee.save()


class ShareCode(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
    )
    can_edit = models.BooleanField(default=False)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )
    expiry = models.DateTimeField(
        default=_get_sharecode_expiry,
        editable=False,
    )

    def __str__(self):
        return str(self.id)

    @transaction.atomic
    def add_user(self, user):
        share = BudgetShare(
            budget=self.budget,
            user=user,
            can_edit=self.can_edit,
            added_by=self.added_by,
        )
        share.clean()
        share.save()
        self.delete()


def export_data(user):
    budgets = Budget.objects.filter(user=user).all()
    export = []
    for budget in budgets:
        payee_export = []
        for payee in budget.payee_set.all():
            payment_export = []
            for payment in payee.payment_set.all():
                payment_export.append({
                    'amount': str(payment.amount),
                    'date': str(payment.date),
                    'pending': payment.pending,
                    'notes': payment.notes,
                })
            payee_export.append({
                'name': payee.name,
                'description': payee.description,
                'payments': payment_export,
            })
        export.append({
            'name': budget.name,
            'description': budget.description,
            'active': budget.active,
            'payees': payee_export,
        })
    return export

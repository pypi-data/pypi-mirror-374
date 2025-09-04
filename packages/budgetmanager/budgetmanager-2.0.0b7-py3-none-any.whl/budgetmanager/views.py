# pylint: disable=no-member,unused-argument
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from . import (
    models,
    permissions,
    serializers,
)
from .metadata import JoinBudgetMetadata
from .pagination import Pagination


class TotalView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(
            f'{models.Payment.get_total(request.user):.2f}'
        )


class ExportView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(models.export_data(request.user))


class PaymentRelatedMixin:
    @action(methods=('GET',), detail=True)
    def total(self, request, pk):
        return Response(
            f'{self.get_object().total:.2f}'
        )


class PartialListMixin:
    list_serializer_class = None

    def get_serializer_class(self):
        assert self.list_serializer_class is not None, (
            f'{self.__class__.__name__} is missing a list_serializer_class attribute'
        )
        if self.action == 'list':
            return self.list_serializer_class
        return self.serializer_class


class BudgetViewSet(PartialListMixin, PaymentRelatedMixin, ModelViewSet):
    queryset = models.Budget.objects
    serializer_class = serializers.BudgetSerializer
    list_serializer_class = serializers.BudgetListSerializer
    permission_classes = (IsAuthenticated, permissions.IsBudgetOwner)
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('active',)
    ordering_fields = ('name', 'id', 'last_used')
    search_fields = ('name',)

    def get_queryset(self):
        return self.queryset.filter(
            Q(user=self.request.user) |
            Q(id__in=self.request.user.budgetshare_set.values('budget_id'))
        ).all()

    @action(methods=('POST',), detail=True, url_path='csv')
    def add_from_csv(self, request, pk):
        self.get_object().add_from_csv(request.data['csv'])
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',), detail=True, url_path='edit')
    def can_edit(self, request, pk):
        return Response(self.get_object().has_access(request.user, True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetShareViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = models.BudgetShare.objects
    serializer_class = serializers.BudgetShareSerializer
    permission_classes = (IsAuthenticated, permissions.CanAccessBudgetShare)
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('budget', 'user')

    def get_queryset(self):
        return self.queryset.filter(
            Q(user=self.request.user) |
            Q(budget__user=self.request.user)
        ).all()

    @action(methods=('POST',), detail=True, url_path='transfer')
    def make_budget_owner(self, request, pk):
        self.get_object().transfer_budget()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class PayeeViewSet(PartialListMixin, PaymentRelatedMixin, ModelViewSet):
    queryset = models.Payee.objects
    serializer_class = serializers.PayeeSerializer
    list_serializer_class = serializers.PayeeListSerializer
    permission_classes = (IsAuthenticated, permissions.IsPayeeOwner)
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('budget',)
    ordering_fields = ('name', 'id', 'last_used')
    search_fields = ('name',)

    def get_queryset(self):
        return self.queryset.filter(
            Q(budget__user=self.request.user) |
            Q(budget_id__in=self.request.user.budgetshare_set.values('budget_id'))
        ).all()

    @action(methods=('GET',), detail=True, url_path='edit')
    def can_edit(self, request, pk):
        return Response(self.get_object().budget.has_access(request.user, True))


class PaymentViewSet(PartialListMixin, ModelViewSet):
    queryset = models.Payment.objects
    list_serializer_class = serializers.PaymentListSerializer
    serializer_class = serializers.PaymentSerializer
    permission_classes = (IsAuthenticated, permissions.IsPaymentOwner)
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = {
        'payee': ('exact',),
        'payee__budget': ('exact',),
        'pending': ('exact',),
        'amount': ('exact', 'gt', 'lt'),
        'date': ('exact', 'gt', 'lt'),
    }
    ordering_fields = ('amount', 'date', 'id')

    def get_queryset(self):
        return self.queryset.filter(
            Q(payee__budget__user=self.request.user) |
            Q(payee__budget_id__in=self.request.user.budgetshare_set.values('budget_id'))
        ).all()

    @action(methods=('GET',), detail=True, url_path='edit')
    def can_edit(self, request, pk):
        return Response(self.get_object().payee.budget.has_access(request.user, True))


class ShareCodeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = models.ShareCode.objects
    serializer_class = serializers.ShareCodeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get_queryset(self):
        return self.queryset.filter(
            Q(budget__user=self.request.user) |
            Q(budget_id__in=self.request.user.budgetshare_set.values('budget_id'))
        )


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = models.Budget.get_user_model().objects
    serializer_class = serializers.UserSerializer
    pagination_class = Pagination

    def get_queryset(self):
        if (self.request.user.is_anonymous):
            return self.queryset.none()
        return self.queryset.filter(
            Q(id=self.request.user.id) |
            Q(id__in=models.BudgetShare.objects.filter(
                budget__user=self.request.user
            ).values('user_id')) |
            Q(id__in=models.BudgetShare.objects.filter(
                user=self.request.user
            ).values('budget__user_id'))
        )

    @action(methods=('GET',), detail=False, url_path='me')
    def get_current_user(self, request):
        if (request.user.is_anonymous):
            return Response(None, status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    # Login,logout adapted from Grvs44/Inclusive-Venues
    @action(methods=('POST',), detail=False)
    def login(self, request):
        '''Log in user'''
        user = authenticate(
            request,
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        if user is None:
            return Response({'detail': 'Incorrect username or password'}, status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(methods=('POST',), detail=False)
    def logout(self, request):
        '''Log out current user'''
        if request.user.is_authenticated:
            logout(request)
            return Response(None, status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Not logged in'}, status.HTTP_401_UNAUTHORIZED)


class JoinBudgetView(APIView):
    permission_classes = (IsAuthenticated,)
    metadata_class = JoinBudgetMetadata

    def post(self, request):
        try:
            get_object_or_404(
                models.ShareCode,
                pk=request.data.get('id')
            ).add_user(request.user)
            return Response(None, status.HTTP_204_NO_CONTENT)
        except DjangoValidationError as e:
            raise RestValidationError(
                detail={'detail': '\n'.join(e)}) from e
        except IntegrityError as e:
            raise RestValidationError(
                {'detail': 'You have already joined this budget'}) from e

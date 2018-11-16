import json
import datetime

from django.http import JsonResponse
from django.contrib.auth.models import ContentType
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, DetailView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core import serializers as django_serializers
from pandas import DataFrame

from lib.revision_log import change
from lib.pagination import MyPageNumberPagination
from .filter import *
from .serializers import *
from usercenter.permission import check_object_perm


class PurchaseView(TemplateView):
    """采购订单视图"""
    template_name = 'costcenter/purchase.html'

    def get_context_data(self, **kwargs):
        context = super(PurchaseView, self).get_context_data(**kwargs)
        try:
            content_type_id = ContentType.objects.get(
                app_label=Purchase._meta.app_label,
                model=Purchase._meta.object_name
            ).id
            context['content_type_id'] = content_type_id
        except Exception as error:
            print(str(error))
            pass
        return context


class PurchaseList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView, DetailView):
    """采购订单列表、新增"""
    queryset = Purchase.objects.all().exclude(is_delete=True).order_by('-id')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = PurchaseFilter
    pagination_class = MyPageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PurchaseDetailSerializer
        else:
            return PurchaseSerializer

    @check_object_perm(codename='costcenter.add_purchase')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='costcenter.add_purchase')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PurchaseDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    """采购订单读取、更新、删除"""
    queryset = Purchase.objects.all().exclude(is_delete=True)
    serializer_class = PurchaseSerializer

    @check_object_perm(codename='costcenter.add_purchase')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='costcenter.change_purchase')
    @change(choice={'status': 'STATUS_CHOICES', 'purchase_type': 'PURCHASE_TYPE_CHOICES'})
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='costcenter.delete_purchase')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class GoodsTypeList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView, DetailView):
    """物品类型列表、新增"""
    queryset = GoodsType.objects.all().exclude(is_delete=True).order_by('-id')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    pagination_class = MyPageNumberPagination
    serializer_class = GoodsTypeSerializer

    @check_object_perm(codename='costcenter.add_goodstype')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_object_perm(codename='costcenter.add_goodstype')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GoodsTypeDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    """物品类型读取、更新、删除"""
    queryset = GoodsType.objects.all().exclude(is_delete=True)
    serializer_class = GoodsTypeSerializer

    @check_object_perm(codename='costcenter.add_goodstype')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_object_perm(codename='costcenter.change_goodstype')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_object_perm(codename='costcenter.delete_goodstype')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


def get_model_frame(start=None, end=None):
    purchase_obj = Purchase.objects.filter(status=5)
    if start and end:
        start_date = datetime.datetime.strptime(start.strip(), '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end.strip(), '%Y-%m-%d')
        purchase_obj = purchase_obj.filter(application_date__range=(start_date, end_date))
    data = []
    serialize_data = django_serializers.serialize("json", purchase_obj)
    frame_data = DataFrame(json.loads(serialize_data), columns=['fields'])['fields'].values.tolist()
    return frame_data

@login_required
def amount_by_department(request):
    start = request.GET.get('start_date', None)
    end = request.GET.get('end_date', None)
    number = request.GET.get('number', None)
    frame_data = get_model_frame(start, end)
    group_by_department = DataFrame(frame_data, columns=['department', 'total_price']).groupby('department')
    frame_result = group_by_department.sum(groupby='total_price').sort_values(
        by = 'total_price',axis = 0,ascending = True)
    if number:
        frame_result = frame_result[-int(number):]
    data_dict = frame_result.to_dict()['total_price']
    name_list = []
    data_list = []
    for i in data_dict:
        name_list.append(i)
        data_list.append({"name": i, "value": round(data_dict[i], 2)})
    result = {
        "name_list": name_list,
        "data_list": data_list
    }
    return JsonResponse(result)

@login_required
def amount_by_type(request):
    start = request.GET.get('start_date', None)
    end = request.GET.get('end_date', None)
    frame_data = get_model_frame(start, end)
    group_by = DataFrame(frame_data, columns=['type', 'total_price']).groupby('type')
    data_result = group_by.sum().to_dict()['total_price']
    name_list = []
    data_list = []
    for i in data_result:
        type_name = GoodsType.objects.get(id=int(i)).name
        name_list.append(type_name)
        data_list.append({"name": type_name, "value": round(data_result[i], 2)})
    result = {
        "name_list": name_list,
        "data_list": data_list
    }
    return JsonResponse(result)

@login_required
def amount_by_purchase_type(request):
    start = request.GET.get('start_date', None)
    end = request.GET.get('end_date', None)
    frame_data = get_model_frame(start, end)
    group_by = DataFrame(frame_data, columns=['purchase_type', 'total_price']).groupby('purchase_type')
    data_result = group_by.sum().to_dict()['total_price']
    name_list = []
    data_list = []
    type_choices = {
        1: '新购',
        2: '续费',
        3: '升级'
    }
    for i in data_result:
        type_name = type_choices[int(i)]
        name_list.append(type_name)
        data_list.append({"name": type_name, "value": round(data_result[i], 2)})
    result = {
        "name_list": name_list,
        "data_list": data_list
    }
    return JsonResponse(result)

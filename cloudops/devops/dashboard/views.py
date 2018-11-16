# -*- coding: utf-8 -*-
from django.utils import timezone
from dashboard.aliyun import ALiYun
from opscenter.models import Support
from dashboard.models import RDSInstance
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect


def aliyun_instance_monitordata(request):
    supports = Support.objects.filter(name__icontains='阿里云').values_list('id', flat=True)
    print(list(set(supports)))
    monitordata = []
    min_keys = 'MySQL_NetworkTraffic,MySQL_QPSTPS,MySQL_IOPS,MySQL_Sessions,MySQL_RowDML'
    hour_keys = 'MySQL_MemCpuUsage,MySQL_DetailedSpaceUsage'
    starttime = (timezone.now() - timezone.timedelta(minutes=5)).isoformat(timespec='minutes').replace("+00:00", "Z")
    endtime = (timezone.now()).isoformat(timespec='minutes').replace("+00:00", "Z")
    print(starttime, endtime)
    if supports:
        for support_id in supports:
            region_id = RDSInstance.objects.filter(support_id=support_id).values_list('region_id', flat=True)
            print(list(set(region_id)))
            if region_id:
                for id in list(set(region_id)):
                    client = ALiYun(support_id, id)
                    instance_id = RDSInstance.objects.filter(region_id=id).values_list('instance_id', flat=True)
                    print(list(set(instance_id)))
                    for id in list(set(instance_id)):
                        instance_monitor = client.get_instance_monitordata(id, min_keys, starttime, endtime)
                        if instance_monitor:
                            monitordata.append(instance_monitor)
    return JsonResponse({'result': monitordata})

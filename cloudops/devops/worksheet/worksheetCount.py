from .models import *
from django.db.models import Q


class GetWorksheetCount(object):

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def worksheet_total_count(self):
        try:
            total_count = WorkSheet.objects.filter(c_time__range=(self.start_date, self.end_date)).count()
        except Exception as e:
            print("The total number of statistical worksheet is abnormal, Error : " + str(e))
            total_count = 0
        return total_count

    def worksheet_solve_count(self):
        count = 0
        try:
            obj = WorkSheet.objects.filter(c_time__range=(self.start_date, self.end_date))
            for i in obj:
                if i.f_time:
                    count += 1
                else:
                    continue
        except Exception as e:
            print("The solve number of statistical worksheet is abnormal, Error : " + str(e))
        return count

    def worksheet_close_count(self):
        try:
            count = WorkSheet.objects.filter(c_time__range=(self.start_date, self.end_date), status=0).count()
        except Exception as e:
            print("The solve number of statistical worksheet is abnormal, Error : " + str(e))
            count = 0
        return count

    def type_count(self):
        """
        @author: 谢育政
        @note: 获取各个类型的工单个数
        :return: 字典: key = 类型, value = 工单个数
        """
        count_dict = {}
        type_obj = WorkSheetType.objects.all()
        for the_type in type_obj:
            try:
                count = WorkSheet.objects.filter(
                    type=the_type.id, c_time__range=(self.start_date, self.end_date)).count()
                if count == 0:
                    continue
                count_dict[the_type.type_name] = count
            except Exception as e:
                print("The classify number of statistical worksheet is abnormal, Error : " + str(e))
                continue
        return count_dict

    def source_count(self, source_list):
        """
        @author: 谢育政
        @note: 获取各个来源的工单个数
        :param source_list: 来源列表, 必须是一个list
        :return: 字典: key = 来源, value = 来源工单个数
        """
        count_dict = {}
        try:
            for source in source_list:
                try:
                    count = WorkSheet.objects.filter(
                        c_time__range=(self.start_date, self.end_date), source=source).count()
                    if count == 0:
                        continue
                    count_dict[source] = count
                except Exception as e:
                    print("The source number of statistical worksheet is abnormal, Error : " + str(e))
                    continue
        except Exception as e:
            print("The source number of statistical worksheet is abnormal, Error : " + str(e))
        return count_dict

    def response_time_count(self):
        valid_worksheet_count = 0
        worksheet_total_time = 0
        count = {
            "one_hours": 0,
            "one_to_eight_hours": 0,
            "eight_to_one_day": 0,
            "more_than_one_day": 0,
            "average": 0
        }
        try:
            obj = WorkSheet.objects.filter(Q(status=2) | Q(status=3) | Q(status=0),
                                           c_time__range=(self.start_date, self.end_date))
            for i in obj:
                try:
                    if i.a_time:
                        if i.p_time:
                            start_time = i.p_time
                        else:
                            start_time = i.c_time
                        end_time = i.a_time
                        delta = end_time - start_time
                        hours = delta.seconds / 60 / 60
                        if delta.days > 1:
                            count["more_than_one_day"] += 1
                        elif hours > 8:
                            count["eight_to_one_day"] += 1
                        elif hours > 1:
                            count["one_to_eight_hours"] += 1
                        else:
                            count["one_hours"] += 1
                        worksheet_total_time += hours
                        valid_worksheet_count += 1
                    else:
                        continue
                except Exception as e:
                    print("The response time of statistical worksheet is abnormal, Error : " + str(e))
                    continue
        except Exception as e:
            print("The response time of statistical worksheet is abnormal, Error : " + str(e))
            pass
        try:
            if valid_worksheet_count != 0 and worksheet_total_time != 0:
                count['average'] = round((worksheet_total_time / valid_worksheet_count), 2)
        except Exception as e:
            print("The response time of statistical worksheet is abnormal, Error : " + str(e))
            pass
        return count

    def solve_time_count(self):
        valid_worksheet_count = 0
        worksheet_total_time = 0
        count = {
            "one_hours": 0,
            "one_to_eight_hours": 0,
            "eight_to_one_day": 0,
            "more_than_one_day": 0,
            "average": 0
        }
        try:
            obj = WorkSheet.objects.filter(Q(status=3) | Q(status=0), c_time__range=(self.start_date, self.end_date))
            for i in obj:
                try:
                    if i.f_time and i.a_time:
                        start_time = i.a_time
                        end_time = i.f_time
                        delta = end_time - start_time
                        hours = delta.seconds / 60 / 60
                        if delta.days > 1:
                            count["more_than_one_day"] += 1
                        elif hours > 8:
                            count["eight_to_one_day"] += 1
                        elif hours > 1:
                            count["one_to_eight_hours"] += 1
                        else:
                            count["one_hours"] += 1
                        worksheet_total_time += hours
                        valid_worksheet_count += 1
                    else:
                        continue
                except Exception as e:
                    print("The solve time of statistical worksheet is abnormal, Error : " + str(e))
                    continue
        except Exception as e:
            print("The solve time of statistical worksheet is abnormal, Error : " + str(e))
            pass
        try:
            if valid_worksheet_count != 0 and worksheet_total_time != 0:
                count['average'] = round((worksheet_total_time / valid_worksheet_count), 2)
        except Exception as e:
            print("The solve time of statistical worksheet is abnormal, Error : " + str(e))
            pass
        return count


class GetWorksheetTotalCount(object):

    def __init__(self):
        pass

    def total_count(self):
        count = 0
        try:
            count = WorkSheet.objects.count()
        except Exception as e:
            print("The total of statistical worksheet is abnormal, Error : " + str(e))
            pass
        finally:
            return count

    def solve_count(self):
        count = 0
        try:
            obj = WorkSheet.objects.all()
            for i in obj:
                if i.f_time:
                    count += 1
                else:
                    continue
        except Exception as e:
            print("The solve total of statistical worksheet is abnormal, Error : " + str(e))
            pass
        finally:
            return count

    def close_count(self):
        count = 0
        try:
            count = WorkSheet.objects.filter(status=0).count()
        except Exception as e:
            print("The close total of statistical worksheet is abnormal, Error : " + str(e))
            pass
        finally:
            return count

    def solved_complete_count(self):
        count = 0
        try:
            count = WorkSheet.objects.filter(Q(result=1)|Q(result=3)|Q(result=4),status=0).count()
        except Exception as e:
            print("The solved complete total of statistical worksheet is abnormal, Error : " + str(e))
            pass
        finally:
            return count

    def process_count(self):
        count = 0
        try:
            count = WorkSheet.objects.filter(Q(status=0)|Q(status=3)).count()
        except Exception as e:
            print("The process total of statistical worksheet is abnormal, Error : " + str(e))
            pass
        finally:
            return count


    def response_time_count(self):
        avg_response_time = 0
        valid_worksheet_count = 0
        worksheet_total_time = 0
        try:
            obj = WorkSheet.objects.all().exclude(Q(status=4) | Q(status=1))
            for i in obj:
                try:
                    if i.a_time:
                        if i.p_time:
                            start_time = i.p_time
                        else:
                            start_time = i.c_time
                        end_time = i.a_time
                        delta = end_time - start_time
                        hours = delta.seconds / 60 / 60
                        worksheet_total_time += hours
                        valid_worksheet_count += 1
                    else:
                        continue
                except Exception as e:
                    print("The response time of statistical worksheet is abnormal, Error : " + str(e))
                    continue
        except Exception as e:
            print("The response time of statistical worksheet is abnormal, Error : " + str(e))
            pass
        try:
            if valid_worksheet_count != 0 and worksheet_total_time != 0:
                avg_response_time = round((worksheet_total_time / valid_worksheet_count), 2)
        except Exception as e:
            print("The response time of statistical worksheet is abnormal, Error : " + str(e))
            pass
        return avg_response_time

    def solve_time_count(self):
        avg_solve_time = 0
        valid_worksheet_count = 0
        worksheet_total_time = 0
        try:
            obj = WorkSheet.objects.all().exclude(Q(status=4) | Q(status=1) | Q(status=2))
            for i in obj:
                try:
                    if i.f_time and i.a_time:
                        start_time = i.a_time
                        end_time = i.f_time
                        delta = end_time - start_time
                        hours = delta.seconds / 60 / 60
                        worksheet_total_time += hours
                        valid_worksheet_count += 1
                    else:
                        continue
                except Exception as e:
                    print("The solve time of statistical worksheet is abnormal, Error : " + str(e))
                    continue
        except Exception as e:
            print("The solve time of statistical worksheet is abnormal, Error : " + str(e))
            pass
        try:
            if valid_worksheet_count != 0 and worksheet_total_time != 0:
                avg_solve_time = round((worksheet_total_time / valid_worksheet_count), 2)
        except Exception as e:
            print("The solve time of statistical worksheet is abnormal, Error : " + str(e))
            pass
        return avg_solve_time

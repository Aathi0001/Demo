from collections import OrderedDict

from datetime import date
from datetime import timedelta

from django.db.models import Count


def get_timeline_years(
    self,
    user
):

    years = (

        WorkLog.objects

        .filter(

            user=user,

            delete_status=False

        )

        .values(

            "work_date__year"

        )

        .annotate(

            total_logs=Count(
                "worklog_id"
            )

        )

        .order_by(

            "-work_date__year"

        )

    )

    return [

        {

            "year":
            item["work_date__year"],

            "total_logs":
            item["total_logs"]

        }

        for item in years

    ]


def get_timeline(
    self,
    user,
    year
):

    worklogs = (

        WorkLog.objects

        .filter(

            user=user,

            delete_status=False,

            work_date__year=year

        )

        .order_by(

            "-work_date"

        )

    )

    today = date.today()

    current_week_start = (

        today -

        timedelta(
            days=today.weekday()
        )

    )

    months = OrderedDict()

    weeks = {}

    for worklog in worklogs:

        work_date = worklog.work_date

        week_start = (

            work_date -

            timedelta(
                days=work_date.weekday()
            )

        )

        week_end = (

            week_start +

            timedelta(days=6)

        )

        week_key = week_start.isoformat()

        month_key = (

            week_start.month,

            week_start.strftime("%B")

        )

        if month_key not in months:

            months[month_key] = {

                "month":
                week_start.month,

                "month_name":
                week_start.strftime("%B"),

                "total_logs":0,

                "weeks":[]

            }

        if week_key not in weeks:

            week_offset = (

                week_start -

                current_week_start

            ).days // 7

            week = {

                "week_start":
                week_start,

                "week_end":
                week_end,

                "week_offset":
                week_offset,

                "log_count":0

            }

            weeks[week_key] = week

            months[month_key][
                "weeks"
            ].append(
                week
            )

        weeks[
            week_key
        ][
            "log_count"
        ] += 1

        months[
            month_key
        ][
            "total_logs"
        ] += 1

    return {

        "year":year,

        "months":
        list(
            months.values()
        )

    }



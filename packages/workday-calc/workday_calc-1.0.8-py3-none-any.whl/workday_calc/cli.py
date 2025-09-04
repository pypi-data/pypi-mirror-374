import arrow
import jpholiday
import os
import workdays

from argparse import ArgumentParser


def parser():
    usage = (
        f'python3 {format(os.path.basename(__file__))} '
        '-s <date> (-e <date> | -n <workdays>) [option]\n'
        'Available date formats is following:\n'
        'YYYY-MM-DD, YYYY-M-DD, YYYY-M-D, YYYY/MM/DD, YYYY/M/DD, '
        'YYYY/M/D, YYYY.MM.DD, YYYY.M.DD, YYYY.M.D, YYYYMMDD'
    )
    argparser = ArgumentParser(usage=usage)

    date_group = argparser.add_argument_group("date")
    date_group.add_argument(
        '--start', '-s', type=str, dest='start_date',
        default=arrow.now(), required=False,
        help='Start date. Default: now'
    )

    mode_group = argparser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--end', '-e', type=str, dest='end_date', required=False,
        help='End date (count workdays between start and end).'
    )
    mode_group.add_argument(
        '--offset-workdays', '-n', type=int, dest='offset_workdays', required=False,
        help='Number of workdays to offset from start_date (inclusive). '
             'Positive moves forward; negative moves backward.'
    )

    date_group.add_argument(
        '--holidays', nargs="*", type=str, default=False, required=False,
        help='Additional holidays (date strings, space-delimited).'
    )

    # 期間文字列を出したい場合のオプション（任意）
    argparser.add_argument(
        '--show-period', '-R', action='store_true', required=False,
        help='In -n mode, also print "period: <start> - <target>".'
    )

    argparser.add_argument(
        '--with-holiday', '-w', dest='with_holiday', action='store_true', required=False,
        help='Use calendar days instead of workdays when counting between -s and -e.'
    )
    argparser.add_argument(
        '--debug', action='store_true', required=False,
        help='Debug option: print detected holidays.'
    )
    args = argparser.parse_args()
    return args


def _parse_start(start_value):
    if isinstance(start_value, arrow.arrow.Arrow):
        return start_value
    return arrow.get(start_value)


def _collect_holidays_between(a: arrow.Arrow, b: arrow.Arrow, extra_args):
    jphd = jpholiday.between(a.datetime, b.datetime)
    holidays = [arrow.get(d[0].strftime("%Y/%m/%d")) for d in jphd]
    if extra_args:
        arg_holiday = [arrow.get(h) for h in extra_args]
        holidays = holidays + arg_holiday
    return holidays, jphd


def workdays_calc(args):
    start_date = _parse_start(args.start_date)
    print(f'start_date: {start_date.format("YYYY/MM/DD")}')

    # --- -n: 開始日を数に含める INCLUSIVE ---
    if args.offset_workdays is not None:
        n = args.offset_workdays
        print(f'offset_workdays: {n} days')

        # 進む方向に応じて十分なバッファで祝日収集
        weeks = (abs(n) // 5) + 2
        far_date = start_date.shift(weeks=weeks if n >= 0 else -weeks)

        holidays, jphd = _collect_holidays_between(
            start_date if n >= 0 else far_date,
            far_date if n >= 0 else start_date,
            args.holidays
        )

        # inclusive: 「開始日=1日目」なので、workdays.workday の 0-index に合わせて 1 つ詰める
        if n > 0:
            n_adj = n - 1
        elif n < 0:
            n_adj = n + 1
        else:
            n_adj = 0  # 0 日なら開始日

        target = workdays.workday(start_date, n_adj, holidays=holidays)
        target_arrow = arrow.get(target)
        print(f'target_date: {target_arrow.format("YYYY/MM/DD")}')

        if args.show_period:
            print(f'period: {start_date.format("YYYY/MM/DD")} - {target_arrow.format("YYYY/MM/DD")}')

        if args.debug:
            print('holidays:')
            for d in jphd:
                print(d)
        return

    # --- -e: 期間の営業日数カウント（両端含む INCLUSIVE） ---
    end_date = arrow.get(args.end_date)
    print(f'end_date: {end_date.format("YYYY/MM/DD")}')
    if args.with_holiday:
        # カレンダー日数は従来通り両端含む
        print(f'days: {(end_date - start_date).days + 1} days')
    else:
        holidays, jphd = _collect_holidays_between(start_date, end_date, args.holidays)
        days = workdays.networkdays(start_date, end_date, holidays=holidays)
        print(f'workdays: {days} days')
        if args.debug:
            print('holidays:')
            for d in jphd:
                print(d)


def main():
    args = parser()
    workdays_calc(args)


if __name__ == "__main__":
    main()

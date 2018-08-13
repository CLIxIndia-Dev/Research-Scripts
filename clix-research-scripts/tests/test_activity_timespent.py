import datetime
import json

import pytest

from activity_timespent import count_events_by_date,\
    filter_activities_by_date,\
    extract_name,\
    get_activities_by_date,\
    get_activity_timestamps_by_date,\
    serialize_datetime,\
    user_log_file_in,\
    get_user_log_filename,\
    get_buddy_id,\
    get_all_dates_from_data


class TestCountEventsByDate(object):
    def test_returns_correct_count(self):
        user_row = [{
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=1)
        }, {
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=2)
        }, {
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=1)
        }]
        date = datetime.date(year=1999, month=1, day=1)
        assert count_events_by_date(user_row, date) == 2

    def test_returns_no_matches_as_zero(self):
        user_row = [{
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=1)
        }, {
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=2)
        }, {
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=1)
        }]
        date = datetime.date(year=1999, month=1, day=3)
        assert count_events_by_date(user_row, date) == 0


class TestExtractName(object):
    def test_can_extract_activity_name(self):
        blob = {
            '_type': 'activity',
            'unit': 'foo',
            'lesson': 'bar',
            'activity': 'bim'
        }
        result = extract_name(blob)
        assert result == 'foo / bar / bim'

    def test_can_extract_tool_name(self):
        blob = {
            '_type': 'tool',
            'app_name': 'zim'
        }
        result = extract_name(blob)
        assert result == 'zim'

    def test_returns_none_for_unknown(self):
        blob = {
            '_type': 'zoink',
            'app_name': 'zim'
        }
        result = extract_name(blob)
        assert result is None


class TestFilterActivitiesByDate(object):
    def test_returns_all_activities_on_given_date(self):
        user_row = [{
            'id': 1,
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=1)
        }, {
            'id': 2,
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=2)
        }, {
            'id': 3,
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=1)
        }, {
            'id': 3,
            'visited_on': datetime.datetime(year=1999,
                                            month=1,
                                            day=1)
        }]
        date = datetime.date(year=1999, month=1, day=1)
        results = filter_activities_by_date(user_row, date)
        assert len(results) == 3
        assert results[0]['id'] == 1
        assert results[1]['id'] == 3
        assert results[2]['id'] == 3


@pytest.fixture(scope="function")
def get_activities_by_date_test_fixture(request):
    request.cls.user_row = [{
        '_type': 'activity',
        'unit': 'foo',
        'lesson': 'bar',
        'activity': 'bim',
        'visited_on': datetime.datetime(year=1999,
                                        month=1,
                                        day=1)
    }, {
        '_type': 'tool',
        'app_name': 'zoom',
        'visited_on': datetime.datetime(year=1999,
                                        month=1,
                                        day=2)
    }, {
        '_type': 'tool',
        'app_name': 'zim',
        'visited_on': datetime.datetime(year=1999,
                                        month=1,
                                        day=1)
    }, {
        '_type': 'tool',
        'app_name': 'zim',
        'visited_on': datetime.datetime(year=1999,
                                        month=1,
                                        day=1)
    }]


@pytest.mark.usefixtures("get_activities_by_date_test_fixture")
class TestGetActivitiesByDate(object):
    def test_returns_only_activity_names(self):
        date = datetime.date(year=1999, month=1, day=1)
        results = get_activities_by_date(self.user_row, date)
        assert isinstance(results, basestring)
        assert 'foo / bar / bim' in results
        assert 'zim' in results
        assert results.count('zim') == 1
        assert 'zoom' not in results

    def test_multiple_activities_are_newline_separated(self):
        date = datetime.date(year=1999, month=1, day=1)
        results = get_activities_by_date(self.user_row, date)
        assert results == 'foo / bar / bim\r\nzim'


@pytest.fixture(scope="function")
def get_activity_timestamps_by_date_test_fixture(request):
    request.cls.user_row = [{
        '_type': 'activity',
        'unit': 'foo',
        'lesson': 'bar',
        'activity': 'bim',
        'visited_on': datetime.datetime(year=1999,
                                        month=1,
                                        day=1,
                                        hour=1,
                                        minute=2)
    }, {
        '_type': 'activity',
        'unit': 'foo',
        'lesson': 'bar',
        'activity': 'bim',
        'visited_on': datetime.datetime(year=1999,
                                        month=1,
                                        day=1,
                                        hour=1,
                                        minute=5)
    }, {
        '_type': 'tool',
        'app_name': 'zoom',
        'visited_on': datetime.datetime(year=1999,
                                        month=1,
                                        day=2)
    }, {
        '_type': 'tool',
        'app_name': 'zim',
        'visited_on': datetime.datetime(year=1999,
                                        month=1,
                                        day=1,
                                        hour=6,
                                        minute=7),
        'created_at': datetime.datetime(year=1999,
                                        month=1,
                                        day=1,
                                        hour=6,
                                        minute=7)
    }, {
        '_type': 'tool',
        'app_name': 'zim',
        'visited_on': datetime.datetime(year=1999,
                                        month=1,
                                        day=1,
                                        hour=7,
                                        minute=6),
        'created_at': datetime.datetime(year=1999,
                                        month=1,
                                        day=1,
                                        hour=7,
                                        minute=6)
    }]
    request.cls.date = datetime.date(year=1999, month=1, day=1)


@pytest.mark.usefixtures("get_activity_timestamps_by_date_test_fixture")
class TestGetActivityTimestampsByDate(object):
    def test_timestamp_order_matches_activity_order(self):
        """ requires a bit of coordination with get_activities_by_date """
        results = get_activity_timestamps_by_date(self.user_row, self.date)
        activity_timestamps = json.dumps(
            [serialize_datetime(self.user_row[0])['visited_on'],
             serialize_datetime(self.user_row[1])['visited_on']]
        )
        tool_timestamps = json.dumps(
            [serialize_datetime(self.user_row[-2])['visited_on'],
             serialize_datetime(self.user_row[-1])['visited_on']]
        )
        assert results.startswith(activity_timestamps)
        assert results.endswith(tool_timestamps)

    def test_multiple_activity_timestamps_are_newline_separated(self):
        results = get_activity_timestamps_by_date(self.user_row, self.date)
        assert '\r\n' in results
        assert results.count('\r\n') == 1


class TestUserLogFileIn(object):
    def test_matches_user_id_only_format(self):
        files = ['1.json', '1-foo.json', 'bar.json']
        result = user_log_file_in(1, files)
        assert result

    def test_matches_user_id_plus_tool_name_format(self):
        files = ['2.json', '1-foo.json', 'bar-1.json']
        result = user_log_file_in(1, files)
        assert result

    def test_returns_false_if_no_match(self):
        files = ['2.json', 'foo-1.json', '1-bar.exe']
        result = user_log_file_in(1, files)
        assert not result


class TestGetUserLogFilename(object):
    def test_matches_user_id_only_format(self):
        files = ['1.json', '1-foo.json', 'bar.json']
        result = get_user_log_filename(1, files)
        assert result == '1.json'

    def test_matches_user_id_plus_tool_name_format(self):
        files = ['2.json', '1-foo.json', 'bar-1.json']
        result = get_user_log_filename(1, files)
        assert result == '1-foo.json'

    def test_raises_exception_if_no_match(self):
        files = ['2.json', 'foo-1.json', '1-bar.exe']
        with pytest.raises(IOError):
            get_user_log_filename(1, files)


class TestGetBuddyId(object):
    def test_get_buddy_id_from_active_users(self):
        user_list = [('black-bear', 1000),
                     ('brown-bear', 2000)]
        result = get_buddy_id(user_list, 'brown-bear')
        assert result == 2000

        with pytest.raises(LookupError):
            get_buddy_id(user_list, 'black-cat')


class TestGetAllDatesFromData(object):
    def test_returns_all_dates_sorted(self):
        now = datetime.datetime.now()
        past = datetime.datetime.now() - datetime.timedelta(days=5)
        future = datetime.datetime.now() + datetime.timedelta(days=5)
        user_data = {
            'blue-cat': [0, {
                'visited_on': now
            }, {
                'visited_on': past
            }],
            'purple-hippo': [2, {
                'visited_on': future
            }, {
                'visited_on': now
            }, {
                'visited_on': now
            }]}
        result = get_all_dates_from_data(user_data)
        assert len(result) == 3
        assert result == [past.date(), now.date(), future.date()]

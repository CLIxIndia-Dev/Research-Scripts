import json
import pytest

from local_assessment_results_and_logs import get_log_entries,\
    format_file_name_for_single_file_upload,\
    format_file_name,\
    get_attempts


class FakeMC(object):
    """ we need a fake MongoClient object to pass around, with a `find`
    method """
    def __init__(self, data):
        self.data = data

    def __getitem__(self, name):
        return self

    def find(self, query):
        return self.data

    def find_one(self, query):
        return self.data


@pytest.fixture(scope="function")
def get_log_entries_test_fixture(request):
    request.cls.MC = FakeMC([{
        'text': {
            'text': json.dumps({
                'assessmentOfferedId': '123'
            })
        },
        'id': 1
    }, {
        'text': {
            'text': json.dumps({
                'assessmentOfferedId': '1234'
            })
        },
        'id': 2
    }, {
        'text': {
            'text': json.dumps({
                'assessmentOfferedId': '123'
            })
        },
        'id': 3
    }])


@pytest.mark.usefixtures("get_log_entries_test_fixture")
class TestGetLogEntries(object):
    def test_without_offered_id_returns_all_entries(self):
        result = get_log_entries('foo', self.MC)
        assert len(result) == 3
        assert result[0]['id'] == 1
        assert result[1]['id'] == 2
        assert result[2]['id'] == 3

    def test_given_offered_id_filters_entries(self):
        result = get_log_entries('foo', self.MC, assessment_offered_id=1)
        assert len(result) == 0

        result = get_log_entries('foo', self.MC, assessment_offered_id='123')
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['id'] == 3


class TestFormatFilename(object):
    def test_extracts_data_with_correct_extension(self):
        fake_dict = {
            'my_file_wav': {
                'assetContentId': 'fake%3Afoo%40MIT'
            }
        }
        filename = format_file_name(fake_dict)
        assert filename == 'foo.wav'


@pytest.fixture(scope="function")
def format_file_name_single_upload_test_fixture(request):
    request.cls.MC = FakeMC({
        'assetContents': [{
            'genusTypeId': 'foo',
            '_id': '123'
        }]
    })


@pytest.mark.usefixtures("format_file_name_single_upload_test_fixture")
class TestFormatFilenameForSingleFileUpload(object):
    def test_gets_asset_from_repository_service(self):
        fake_dict = {
            'assetId': '0' * 24,
            'assetContentTypeId': 'foo'
        }
        filename = format_file_name_for_single_file_upload(
            fake_dict,
            self.MC
        )
        assert filename == '123.foo'


@pytest.fixture(scope="function")
def get_attempts_test_fixture(request):
    # Yes, this is not a real mocked object...
    # Item + Asset mixed so that we can use a single FakeMC
    request.cls.MC = FakeMC({
        'question': {
            'choices': [{
                'id': '123',
                'texts': [{
                    'text': 'a bear',
                    'languageTypeId': '639-2%3AENG%40ISO'
                }]
            }, {
                'id': '321',
                'texts': [{
                    'text': 'a cat',
                    'languageTypeId': '639-2%3AENG%40ISO'
                }]
            }]
        },
        'assetContents': [{
            'genusTypeId': 'foo',
            '_id': '1234'
        }]
    })


@pytest.mark.usefixtures("get_attempts_test_fixture")
class TestGetAttempts(object):
    def test_throws_exception_for_unknown_response_format(self):
        question = {
            'itemId': '1' * 24,
            'responses': [{
                'bim': 'bap'
            }]
        }
        with pytest.raises(TypeError):
            get_attempts(question, self.MC)

    def test_returns_filename_for_single_file_upload(self):
        question = {
            'itemId': '1' * 24,
            'responses': [{
                'fileId': {
                    'assetId': '0' * 24,
                    'assetContentTypeId': 'foo'
                }
            }]
        }
        attempts = get_attempts(question, self.MC)
        assert attempts == '1234.foo'

    def test_returns_filename_for_multi_file_upload(self):
        question = {
            'itemId': '1' * 24,
            'responses': [{
                'fileIds': {
                    'my_file_wav': {
                        'assetContentId': 'fake%3Afoo%40MIT'
                    }
                }
            }]
        }
        attempts = get_attempts(question, self.MC)
        assert attempts == 'foo.wav'

    def test_returns_choice_text_for_multichoice(self):
        question = {
            'itemId': '1' * 24,
            'responses': [{
                'choiceIds': ['123']
            }]
        }
        attempts = get_attempts(question, self.MC)
        assert attempts == 'a bear'

    def test_returns_no_file_text(self):
        question = {
            'itemId': '1' * 24,
            'responses': [{
                'fileIds': {}
            }]
        }
        attempts = get_attempts(question, self.MC)
        assert attempts == 'empty file response'

    def test_returns_short_answer_text(self):
        question = {
            'itemId': '1' * 24,
            'responses': [{
                'text': {
                    'text': 'a short answer'
                }
            }]
        }
        attempts = get_attempts(question, self.MC)
        assert attempts == 'a short answer'

    def test_returns_none_for_missing_response(self):
        question = {
            'itemId': '1' * 24,
            'responses': [{
                'missingResponse': 0
            }]
        }
        attempts = get_attempts(question, self.MC)
        assert attempts == 'None'

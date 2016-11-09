import random
import pytest
from turbo_palm_tree.utility.parse_arguments import parse_arguments, SubredditSortTypes
import os
import time
from elasticsearch import Elasticsearch, ElasticsearchException
from image_match import SignatureES


class TestClass:
    subreddit_url = "https://www.reddit.com/r/jtaraTest/"
    subreddit_name = "jtaratest"

    @pytest.fixture
    def get_es(self):
        """Return the elasticsearch.Elasticsearch object"""
        es = Elasticsearch()
        return es

    @pytest.fixture
    def get_im(self, get_es):
        """Return the image_match.SignatureES object (requires Elasticsearch object to instantiate)"""
        ses = SignatureES(get_es, distance_cutoff=0.40)
        return ses

    @pytest.fixture
    def get_es_and_im(self, get_es, get_im):
        """Return es object & SignatureES object"""
        return get_es, get_im

    def get_random_parsed_arg(self):
        """Returns a parsed arg with a random sort type"""

        def get_random_sort_type():
            """Return a random sort types drawing from the enum class of all possible sort types"""
            sort_types = list(st.value for st in SubredditSortTypes)
            sort_types.extend(SubredditSortTypes.top.advanced_sorts() +
                              SubredditSortTypes.controversial.advanced_sorts())
            return sort_types[random.randrange(0, len(sort_types))]

        temp_dir = os.path.join(os.getcwd(), 'temp_test_downloads')
        sort_type = get_random_sort_type()
        return (sort_type, 'jtaraTest', temp_dir,
                parse_arguments(['--sort-type', sort_type, self.subreddit_name, temp_dir]))

    def test_parsed_args(self):
        sort_type, sr_name, path, args = self.get_random_parsed_arg()
        assert sort_type == args.sort_type
        assert args.subreddit == sr_name
        assert path == args.directory

    def test_elasticsearch(self, get_es):
        es = get_es
        try:
            for i in range(5):
                es.ping()
        except ElasticsearchException:
            assert False

    def test_image_match(self):
        pass

    def test_duplicate_removal(self):
        pass

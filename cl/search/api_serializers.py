from collections import OrderedDict

from rest_framework import serializers

from cl.audio.models import Audio
from cl.api.utils import DynamicFieldsModelSerializer
from cl.people_db.models import Person, Party
from cl.search.models import Docket, OpinionCluster, Opinion, Court, \
    OpinionsCited, DocketEntry, RECAPDocument


class DocketSerializer(DynamicFieldsModelSerializer,
                       serializers.HyperlinkedModelSerializer):
    court = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='court-detail',
        queryset=Court.objects.exclude(jurisdiction='T'),
    )
    clusters = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='opinioncluster-detail',
        queryset=OpinionCluster.objects.all(),
    )
    audio_files = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='audio-detail',
        queryset=Audio.objects.all(),
    )
    assigned_to = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='person-detail',
        queryset=Person.objects.all(),
    )
    referred_to = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='person-detail',
        queryset=Person.objects.all(),
    )
    parties = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='party-detail',
        queryset=Party.objects.all(),
    )
    absolute_url = serializers.CharField(source='get_absolute_url',
                                         read_only=True)

    class Meta:
        model = Docket
        exclude = ('view_count',)


class RECAPDocumentSerializer(DynamicFieldsModelSerializer,
                              serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RECAPDocument
        fields = '__all__'


class DocketEntrySerializer(DynamicFieldsModelSerializer,
                            serializers.HyperlinkedModelSerializer):
    docket = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='docket-detail',
        queryset=Docket.objects.all(),
    )
    recap_documents = RECAPDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = DocketEntry
        fields = '__all__'


class CourtSerializer(DynamicFieldsModelSerializer,
                      serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Court
        exclude = ('notes',)


class OpinionSerializer(DynamicFieldsModelSerializer,
                        serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.CharField(source='get_absolute_url',
                                         read_only=True)
    cluster = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='opinioncluster-detail',
        queryset=OpinionCluster.objects.all(),
    )
    author = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='person-detail',
        queryset=Person.objects.all(),
    )
    joined_by = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='person-detail',
        queryset=Person.objects.all(),
    )

    class Meta:
        model = Opinion
        fields = '__all__'


class OpinionsCitedSerializer(DynamicFieldsModelSerializer,
                              serializers.HyperlinkedModelSerializer):
    # These attributes seem unnecessary and this endpoint serializes the same
    # data without them, but when they're not here the API does a query that
    # pulls back ALL Opinions.
    citing_opinion = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='opinion-detail',
        queryset=Opinion.objects.all(),
    )
    cited_opinion = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='opinion-detail',
        queryset=Opinion.objects.all(),
    )

    class Meta:
        model = OpinionsCited
        fields = '__all__'


class OpinionClusterSerializer(DynamicFieldsModelSerializer,
                               serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.CharField(source='get_absolute_url',
                                         read_only=True)
    panel = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='person-detail',
        queryset=Person.objects.all(),
    )
    non_participating_judges = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='person-detail',
        queryset=Person.objects.all(),
    )
    docket = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='docket-detail',
        queryset=Docket.objects.all(),
    )
    sub_opinions = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='opinion-detail',
        queryset=Opinion.objects.all(),
    )

    class Meta:
        model = OpinionCluster
        fields = '__all__'


class SearchResultSerializer(serializers.Serializer):
    """The serializer for search results.

    Does not presently support the fields argument.
    """

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError

    solr_field_mappings = {
        u'boolean': serializers.BooleanField,
        u'string': serializers.CharField,
        u'text_en_splitting_cl': serializers.CharField,
        u'text_no_word_parts': serializers.CharField,
        u'date': serializers.DateTimeField,

        # Numbers
        u'int': serializers.IntegerField,
        u'tint': serializers.IntegerField,
        u'long': serializers.IntegerField,
        # schema.SolrFloatField: serializers.FloatField,
        # schema.SolrDoubleField: serializers.IntegerField,

        # Other
        u'pagerank': serializers.CharField,
    }
    skipped_fields = ['_version_', 'django_ct', 'django_id', 'text']

    def get_fields(self):
        """Return a list of fields so that they don't have to be declared one
        by one and updated whenever there's a new field.
        """
        fields = {
            'snippet': serializers.CharField(read_only=True),
        }
        # Map each field in the Solr schema to a DRF field
        for field in self._context['schema']['fields']:
            if field.get('multiValued'):
                drf_field = serializers.ListField
            else:
                drf_field = self.solr_field_mappings[field[u'type']]
            fields[field[u'name']] = drf_field(read_only=True)

        for field in self.skipped_fields:
            if field in fields:
                fields.pop(field)
        fields = OrderedDict(sorted(fields.items()))  # Sort by key
        return fields

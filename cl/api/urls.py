from cl.api import views
from cl.audio import api_views as audio_views
from cl.people_db import api_views as people_views
from cl.search import api_views as search_views

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Search & Audio
router.register(r'dockets', search_views.DocketViewSet)
router.register(r'courts', search_views.CourtViewSet)
router.register(r'audio', audio_views.AudioViewSet)
router.register(r'clusters', search_views.OpinionClusterViewSet)
router.register(r'opinions', search_views.OpinionViewSet)
router.register(r'opinions-cited', search_views.OpinionsCitedViewSet)
router.register(r'search', search_views.SearchViewSet, base_name='search')

# People & Entities
router.register(r'people', people_views.PersonViewSet)
router.register(r'positions', people_views.PositionViewSet)
router.register(r'retention-events', people_views.RetentionEventViewSet)
router.register(r'educations', people_views.EducationViewSet)
router.register(r'schools', people_views.SchoolViewSet)
router.register(r'political-affiliations',
                people_views.PoliticalAffiliationViewSet)
router.register(r'sources', people_views.SourceViewSet)
router.register(r'aba-ratings', people_views.ABARatingViewSet)
router.register(r'parties', people_views.PartyViewSet)


urlpatterns = [
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/rest/(?P<version>[v3]+)/', include(router.urls)),

    # Documentation
    url(r'^api/$',
        views.api_index,
        name='api_index'),
    url(r'^api/jurisdictions/$',
        views.court_index,
        name='court_index'),
    url(r'^api/rest-info/(?P<version>v[123])?/?$',
        views.rest_docs,
        name='rest_docs'),
    url(r'^api/bulk-info/$',
        views.bulk_data_index,
        name='bulk_data_index'),
    url(r'^api/rest/v(?P<version>[123])/coverage/(?P<court>.+)/$',
        views.coverage_data,
        name='coverage_data'),

    # Pagerank file
    url(r'^api/bulk/external_pagerank/$',
        views.serve_pagerank_file,
        name='pagerank_file'),

    # Deprecation Dates:
    # v1: 2016-04-01
    # v2: 2016-04-01
    url(r'^api/rest/v(?P<v>[12])/.*',
        views.deprecated_api,
        name='deprecated_api'),
]

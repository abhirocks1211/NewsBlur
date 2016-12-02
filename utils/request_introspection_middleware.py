from django.conf import settings
from utils import log as logging

class DumpRequestMiddleware:
    def process_request(self, request):
        if settings.DEBUG:
            request_items = request.GET.items()
            if request_items:
                logging.debug("~BC~SBGET~SN ~FK%s" % dict(request_items))
            request_items = request.POST.items()
            if request_items:
                logging.debug("~BC~SBPOST~SN ~FK%s" % dict(request_items))
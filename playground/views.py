import requests
import logging

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
# from django.core.mail import BadHeaderError, EmailMessage

from rest_framework.views import APIView
# from templated_mail.mail import BaseEmailMessage

from .tasks import notify_customers


logger = logging.getLogger(__name__)
logger.info

# Create your views here.
class HelloView(APIView):
    # @method_decorator(cache_page(5*60))
    def get(self, request):
        try:
            logger.info('Calling Httpbin')
            response = requests.get('https://httpbin.org/delay/2')
            logger.info('recieved the info')
            data = response.json()
        except requests.ConnectionError:
            logger.critical('httpbin is offline')
        return render(request, 'hello.html', {'name': data})


# def say_hello(request):
#     try:
#         message = BaseEmailMessage(
#             template_name = 'emails/hello.html',
#             context={'name': 'alex'},
#         )
#         message.send(['bob@alexdev.com'])
#     except BadHeaderError:
#         print('error')
    
#     notify_customers.delay('Hello') 

from django.shortcuts import render
# from django.core.mail import BadHeaderError, EmailMessage
# from templated_mail.mail import BaseEmailMessage
from .tasks import notify_customers

# Create your views here.
def say_hello(request):
    # try:
    #     message = BaseEmailMessage(
    #         template_name = 'emails/hello.html',
    #         context={'name': 'alex'},
    #     )
    #     message.send(['bob@alexdev.com'])
    # except BadHeaderError:
    notify_customers.delay('Hello')
    return render(request, 'hello.html')

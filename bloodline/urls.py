"""bloodline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from blood.views import donation_id, donation_received, donation_start, mci_request_complete, \
    mci_request_start, show_reject, \
    single_request_complete, single_request_confirm, single_request_details, single_request_start
from homepage.views import homepage

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', homepage, name="homepage"),
                  path('donation/', donation_start, name="donation_start"),
                  path('donation/<id_number>', donation_id, name="donation_id"),
                  path('donation/received/<donation_id>', donation_received,
                       name="donation_received"),
                  path('single_request/', single_request_start, name="single_request_start"),
                  path('single_request/<id_number>', single_request_details, name="single_request"),
                  path('single_request/<id_number>/<int:units>', single_request_confirm,
                       name="single_request_confirm"),
                  path('single_request/<request_id>/complete', single_request_complete,
                       name="single_request_complete"),
                  path('mci_request/', mci_request_start, name="mci_request"),
                  path('mci_request/<request_id>/complete', mci_request_complete,
                       name="mci_request_complete"),
                  path('reject/<int:reject_id>', show_reject, name="show_reject"),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

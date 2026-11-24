
from django.urls import path
from . import views
from .report_views import export_rekap_excel

app_name = 'core'

urlpatterns = [

    # HALAMAN UTAMA
    path(
        '',
        views.home,
        name='home'
    ),

    # DETAIL PAKET WISATA
    path(
        'paket/<int:package_id>/',
        views.package_detail,
        name='package_detail'
    ),

    # DETAIL DESTINASI WISATA
    path(
        'destinasi/<int:destination_id>/',
        views.destination_detail,
        name='destination_detail'
    ),

    # FORM BOOKING
    path(
        'booking/',
        views.booking,
        name='booking'
    ),

    # CEK BOOKING PELANGGAN
    path(
        'cek-booking/',
        views.check_booking,
        name='check_booking'
    ),

    # UPLOAD BUKTI PEMBAYARAN
    path(
        'upload-pembayaran/',
        views.upload_payment,
        name='upload_payment'
    ),

    # DASHBOARD ADMIN
    path(
        'panel/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    # DOWNLOAD LAPORAN EXCEL
    path(
        'panel/export-rekap-excel/',
        export_rekap_excel,
        name='export_rekap_excel'
    ),

]

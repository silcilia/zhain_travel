
from urllib.parse import quote
from datetime import datetime
import re
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    BookingInquiry,
    PaymentRecord,
    TourPackage,
    TourDestination,
    Brochure,
    GalleryItem,
    Testimonial,
)


# =====================================================
# DATA LAYANAN WEBSITE
# =====================================================

SERVICES = [
    (
        'Paket Wisata Domestik',
        'Rute wisata Indonesia dengan itinerary yang praktis dan nyaman.'
    ),
    (
        'Open Trip',
        'Gabung perjalanan seru dengan jadwal dan itinerary yang sudah disiapkan.'
    ),
    (
        'Private Tour',
        'Liburan lebih fleksibel bersama keluarga, teman, atau pasangan.'
    ),
    (
        'Family & Company Gathering',
        'Perjalanan untuk bonding, gathering, dan kegiatan perusahaan.'
    ),
    (
        'Study Tour',
        'Kunjungan edukatif dengan perjalanan yang aman dan terorganisir.'
    ),
    (
        'Outbound',
        'Kegiatan team building dan outbound yang seru dan terarah.'
    ),
    (
        'Custom Trip',
        'Itinerary dibuat sesuai kebutuhan, waktu, dan budget perjalanan.'
    ),
    (
        'Transportasi Wisata',
        'Bus, kendaraan wisata, dan transportasi perjalanan sesuai kebutuhan.'
    ),
]


DEFAULT_PACKAGES = [
    (
        'Palembang – Pahawang',
        'Sumatera Selatan & Lampung',
        'domestik',
        0,
        'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1000&q=80'
    ),
    (
        'Wayang Pahawang',
        'Lampung',
        'domestik',
        0,
        'https://images.unsplash.com/photo-1540202404-a2f29016b523?auto=format&fit=crop&w=1000&q=80'
    ),
    (
        'Bangka',
        'Kepulauan Bangka Belitung',
        'domestik',
        0,
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80'
    ),
    (
        'Bali – Lombok',
        'Bali & Nusa Tenggara',
        'domestik',
        0,
        'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1000&q=80'
    ),
    (
        'Bandung',
        'Jawa Barat',
        'domestik',
        0,
        'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1000&q=80'
    ),
    (
        'Bromo',
        'Jawa Timur',
        'domestik',
        0,
        'https://images.unsplash.com/photo-1516690561799-46d8f74f9abf?auto=format&fit=crop&w=1000&q=80'
    ),
    (
        'Yogyakarta',
        'Daerah Istimewa Yogyakarta',
        'domestik',
        0,
        'https://images.unsplash.com/photo-1596402184320-417e7178b2cd?auto=format&fit=crop&w=1000&q=80'
    ),
    (
        'Malaysia',
        'Kuala Lumpur & sekitarnya',
        'internasional',
        0,
        'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?auto=format&fit=crop&w=1000&q=80'
    ),
    (
        'Singapore',
        'Singapore',
        'internasional',
        0,
        'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=1000&q=80'
    ),
    (
        'Thailand – Bangkok',
        'Bangkok, Thailand',
        'internasional',
        0,
        'https://images.unsplash.com/photo-1508009603885-50cf7c579365?auto=format&fit=crop&w=1000&q=80'
    ),
]


# =====================================================
# DATA GALERI DEFAULT
# =====================================================

DEFAULT_GALLERY = [
    (
        'Momen perjalanan',
        'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=1200&q=80'
    ),
    (
        'Liburan pantai',
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80'
    ),
    (
        'Explore Asia',
        'https://images.unsplash.com/photo-1528181304800-259b08848526?auto=format&fit=crop&w=1200&q=80'
    ),
    (
        'Sunrise adventure',
        'https://images.unsplash.com/photo-1516690561799-46d8f74f9abf?auto=format&fit=crop&w=1200&q=80'
    ),
    (
        'City escape',
        'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=1200&q=80'
    ),
    (
        'Island getaway',
        'https://images.unsplash.com/photo-1540202404-a2f29016b523?auto=format&fit=crop&w=1200&q=80'
    ),
]


# =====================================================
# HELPER: NORMALISASI NOMOR TELEPON
# =====================================================

def normalize_phone(phone):
    """
    Menyamakan format nomor telepon agar:
    08xxxxxxxxxx, 628xxxxxxxxxx, dan 8xxxxxxxxxx
    dapat dibandingkan.
    """

    phone = ''.join(
        character
        for character in phone
        if character.isdigit()
    )

    if phone.startswith('0'):
        phone = '62' + phone[1:]

    elif phone.startswith('8'):
        phone = '62' + phone

    return phone


# =====================================================
# HALAMAN BERANDA
# =====================================================

def home(request):
    packages = TourPackage.objects.filter(
        is_active=True
    ).order_by('id')

    package_cards = []

    for package in packages:

        brochure_url = (
            package.brochure.url
            if package.brochure
            else ''
        )

        if not brochure_url:
            related_brochure = package.brochures.filter(
                is_active=True
            ).first()

            if related_brochure and related_brochure.file:
                brochure_url = related_brochure.file.url

        package_cards.append({
            'name': package.name,
            'location': package.destination,
            'tag': package.get_category_display(),
            'image': package.image.url if package.image else '',
            'brochure': brochure_url,
            'id': package.pk,
        })

    # Mengambil seluruh destinasi aktif dari paket aktif.
    destinations = TourDestination.objects.filter(
        package__is_active=True,
        is_active=True
    ).select_related('package').order_by('id')

    # Membaca pilihan paket dan destinasi dari URL.
    # Digunakan ketika pelanggan menekan Booking Sekarang
    # pada halaman detail destinasi.
    selected_package_id = request.GET.get(
        'package_id',
        ''
    )

    selected_destination_id = request.GET.get(
        'destination_id',
        ''
    )

    gallery_items = GalleryItem.objects.filter(
        is_active=True
    )

    if gallery_items.exists():
        gallery = [
            {
                'title': item.title,
                'image': item.image.url,
                'caption': item.caption,
            }
            for item in gallery_items
        ]
    else:
        gallery = [
            {
                'title': title,
                'image': image,
                'caption': '',
            }
            for title, image in DEFAULT_GALLERY
        ]

    brochures = Brochure.objects.filter(
        is_active=True
    )

    testimonials = Testimonial.objects.filter(
        is_active=True
    )

    whatsapp_text = quote(
        'Halo Zhain Tour and Travel, '
        'saya ingin bertanya mengenai paket wisata.'
    )

    whatsapp_url = (
        f'https://wa.me/{settings.WHATSAPP_NUMBER}'
        f'?text={whatsapp_text}'
    )

    context = {
        'packages': package_cards,
        'destinations': destinations,
        'selected_package_id': selected_package_id,
        'selected_destination_id': selected_destination_id,
        'services': SERVICES,
        'gallery': gallery,
        'brochures': brochures,
        'testimonials': testimonials,
        'whatsapp_url': whatsapp_url,
    }

    return render(
        request,
        'core/home.html',
        context
    )


# =====================================================
# DETAIL PAKET WISATA
# =====================================================

def package_detail(request, package_id):

    package = get_object_or_404(
        TourPackage,
        pk=package_id,
        is_active=True
    )

    destinations = package.destinations.filter(
        is_active=True
    ).order_by('id')

    context = {
        'package': package,
        'destinations': destinations,
    }

    return render(
        request,
        'core/package_detail.html',
        context
    )


# =====================================================
# DETAIL DESTINASI
# =====================================================

def destination_detail(request, destination_id):

    destination = get_object_or_404(
        TourDestination,
        pk=destination_id,
        is_active=True
    )

    return render(
        request,
        'core/destination_detail.html',
        {
            'destination': destination,
        }
    )


# =====================================================
# BOOKING DARI WEBSITE
# =====================================================

@require_POST
def booking(request):

    name = request.POST.get(
        'name',
        ''
    ).strip()

    phone = request.POST.get(
        'phone',
        ''
    ).strip()

    email = request.POST.get(
        'email',
        ''
    ).strip()

    package_id = request.POST.get(
        'package_id',
        ''
    ).strip()

    destination_id = request.POST.get(
        'destination_id',
        ''
    ).strip()

    custom_package = request.POST.get(
        'custom_package',
        ''
    ).strip()

    departure_date = request.POST.get(
        'departure_date',
        ''
    ).strip()

    participants_raw = request.POST.get(
        'participants',
        '1'
    ).strip()

    message = request.POST.get(
        'message',
        ''
    ).strip()

    # -------------------------------------------------
    # VALIDASI NAMA DAN NOMOR WHATSAPP
    # -------------------------------------------------

    if not name or not phone:

        messages.error(
            request,
            'Nama dan nomor WhatsApp wajib diisi.'
        )

        return redirect('/#booking')

    phone_errors = validate_booking_contact(
        phone,
        email
    )

    if phone_errors:

        for error in phone_errors.values():
            messages.error(request, error)

        return redirect('/#booking')

    # -------------------------------------------------
    # VALIDASI JUMLAH PESERTA
    # -------------------------------------------------

    try:

        participants = int(participants_raw)

        if participants < 1 or participants > 100:
            raise ValueError

    except (ValueError, TypeError):

        messages.error(
            request,
            'Jumlah peserta harus antara 1 sampai 100 orang.'
        )

        return redirect('/#booking')

    # -------------------------------------------------
    # MENENTUKAN PAKET PERJALANAN
    # -------------------------------------------------

    package_ref = None
    destination_ref = None

    package_name = (
        custom_package
        or 'Konsultasi paket wisata'
    )

    if package_id:

        try:

            package_ref = TourPackage.objects.get(
                pk=package_id,
                is_active=True
            )

            package_name = package_ref.name

        except (
            TourPackage.DoesNotExist,
            ValueError,
            TypeError
        ):

            messages.error(
                request,
                'Paket yang dipilih tidak tersedia. '
                'Silakan pilih kembali.'
            )

            return redirect('/#booking')

    # -------------------------------------------------
    # MENENTUKAN DESTINASI
    # -------------------------------------------------

    destination_name = ''

    if destination_id:

        # Destinasi wajib berasal dari paket yang dipilih.
        if not package_ref:

            messages.error(
                request,
                'Silakan pilih paket perjalanan terlebih dahulu.'
            )

            return redirect('/#booking')

        try:

            destination_ref = TourDestination.objects.get(
                pk=destination_id,
                package=package_ref,
                is_active=True
            )

            destination_name = destination_ref.name

        except (
            TourDestination.DoesNotExist,
            ValueError,
            TypeError
        ):

            messages.error(
                request,
                'Destinasi tidak tersedia atau tidak sesuai '
                'dengan paket yang dipilih.'
            )

            return redirect('/#booking')

    # -------------------------------------------------
    # VALIDASI TANGGAL KEBERANGKATAN
    # -------------------------------------------------

    parsed_date = None

    if departure_date:

        try:

            parsed_date = datetime.strptime(
                departure_date,
                '%Y-%m-%d'
            ).date()

            if parsed_date < timezone.localdate():

                messages.error(
                    request,
                    'Tanggal keberangkatan tidak boleh di masa lalu.'
                )

                return redirect('/#booking')

        except ValueError:

            messages.error(
                request,
                'Format tanggal keberangkatan tidak valid.'
            )

            return redirect('/#booking')

    # -------------------------------------------------
    # SIMPAN BOOKING
    # -------------------------------------------------

    # Harga ditentukan admin setelah konsultasi.
    # package_ref menyimpan paket perjalanan.
    # destination_ref menyimpan destinasi pilihan pelanggan.

    order = BookingInquiry.objects.create(
        name=name,
        phone=phone,
        email=email,
        package_ref=package_ref,
        destination_ref=destination_ref,
        package=package_name,
        departure_date=parsed_date,
        participants=participants,
        package_price_per_person=0,
        total_price=0,
        message=message,
    )

    # -------------------------------------------------
    # MEMBUAT TOKEN AKSES BOOKING
    # -------------------------------------------------

    access_token = str(order.application_token)

    date_text = (
        parsed_date.strftime('%d-%m-%Y')
        if parsed_date
        else 'Belum ditentukan'
    )

    destination_text = (
        destination_name
        if destination_name
        else 'Belum dipilih'
    )

    # -------------------------------------------------
    # MEMBUAT PESAN WHATSAPP
    # -------------------------------------------------

    wa_message = (
        f'Halo Zhain Tour and Travel, '
        f'saya ingin melanjutkan konsultasi booking.\n\n'
        f'Referensi akses booking: {access_token}\n'
        f'Nama: {name}\n'
        f'WhatsApp: {phone}\n'
        f'Email: {email or "-"}\n'
        f'Paket: {package_name}\n'
        f'Destinasi: {destination_text}\n'
        f'Tanggal keberangkatan: {date_text}\n'
        f'Jumlah peserta: {participants} orang\n'
        f'Catatan: {message or "-"}\n\n'
        f'Mohon informasi itinerary dan penawaran harga. '
        f'Terima kasih.'
    )

    whatsapp_url = (
        f'https://wa.me/{settings.WHATSAPP_NUMBER}'
        f'?text={quote(wa_message)}'
    )

    messages.success(
        request,
        'Booking berhasil disimpan. '
        'Simpan token akses booking untuk mengecek pesanan.'
    )

    return redirect(whatsapp_url)


# =====================================================
# VALIDASI KONTAK BOOKING
# =====================================================

def validate_booking_contact(phone, email):

    errors = {}

    phone = phone.strip()

    phone_pattern = r'(?:\+62|0)8[1-9][0-9]{7,11}'

    if not re.fullmatch(phone_pattern, phone):

        errors['phone'] = (
            'Nomor WhatsApp tidak valid. '
            'Contoh: 081234567890 atau +6281234567890.'
        )

    email = email.strip()

    if email:

        try:
            validate_email(email)

        except ValidationError:
            errors['email'] = 'Format alamat email tidak valid.'

    return errors


# =====================================================
# CEK BOOKING PELANGGAN
# =====================================================

def check_booking(request):

    booking = None
    payments = []

    booking_code = ''
    phone = ''
    application_token = ''

    if request.method == 'GET':

        context = {
            'booking': None,
            'payments': [],
            'booking_code': '',
            'phone': '',
            'application_token': '',
        }

        return render(
            request,
            'core/check_booking.html',
            context
        )

    if request.method == 'POST':

        booking_code = request.POST.get(
            'booking_code',
            ''
        ).strip()

        application_token = request.POST.get(
            'application_token',
            ''
        ).strip()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        if not phone or (
            not booking_code and not application_token
        ):

            messages.error(
                request,
                'Masukkan nomor WhatsApp dan kode booking '
                'atau token akses booking.'
            )

        else:

            booking_query = BookingInquiry.objects.all()

            if booking_code:

                booking_data = booking_query.filter(
                    booking_code__iexact=booking_code
                ).first()

            else:

                booking_data = booking_query.filter(
                    application_token=application_token
                ).first()

            if (
                booking_data
                and normalize_phone(booking_data.phone)
                == normalize_phone(phone)
            ):

                booking = booking_data

                payments = booking.payments.all().order_by(
                    '-paid_at'
                )

            else:

                messages.error(
                    request,
                    'Data booking tidak ditemukan. '
                    'Periksa kembali kode/token booking '
                    'dan nomor WhatsApp kamu.'
                )

    context = {
        'booking': booking,
        'payments': payments,
        'booking_code': booking_code,
        'application_token': application_token,
        'phone': phone,
    }

    return render(
        request,
        'core/check_booking.html',
        context
    )


# =====================================================
# UPLOAD BUKTI PEMBAYARAN
# =====================================================

@require_POST
def upload_payment(request):

    booking_code = request.POST.get(
        'booking_code',
        ''
    ).strip()

    application_token = request.POST.get(
        'application_token',
        ''
    ).strip()

    phone = request.POST.get(
        'phone',
        ''
    ).strip()

    amount_raw = request.POST.get(
        'amount',
        ''
    ).strip()

    payment_type = request.POST.get(
        'payment_type',
        ''
    ).strip()

    method = request.POST.get(
        'method',
        'transfer'
    ).strip()

    proof = request.FILES.get('proof')

    # -------------------------------------------------
    # MENCARI BOOKING
    # -------------------------------------------------

    booking_query = BookingInquiry.objects.all()

    if booking_code:

        booking = booking_query.filter(
            booking_code__iexact=booking_code
        ).first()

    elif application_token:

        booking = booking_query.filter(
            application_token=application_token
        ).first()

    else:
        booking = None

    if (
        not booking
        or normalize_phone(booking.phone)
        != normalize_phone(phone)
    ):

        messages.error(
            request,
            'Data booking tidak ditemukan.'
        )

        return redirect('core:check_booking')

    # -------------------------------------------------
    # VALIDASI NOMINAL
    # -------------------------------------------------

    try:

        amount = int(amount_raw)

        if amount <= 0:
            raise ValueError

    except (ValueError, TypeError):

        messages.error(
            request,
            'Nominal pembayaran harus lebih dari Rp0.'
        )

        return redirect('core:check_booking')

    # -------------------------------------------------
    # VALIDASI JENIS PEMBAYARAN
    # -------------------------------------------------

    allowed_payment_types = [
        'dp',
        'installment',
        'settlement',
    ]

    if payment_type not in allowed_payment_types:

        messages.error(
            request,
            'Jenis pembayaran tidak valid.'
        )

        return redirect('core:check_booking')

    # -------------------------------------------------
    # VALIDASI METODE PEMBAYARAN
    # -------------------------------------------------

    allowed_methods = [
        'transfer',
        'cash',
        'qris',
        'other',
    ]

    if method not in allowed_methods:

        messages.error(
            request,
            'Metode pembayaran tidak valid.'
        )

        return redirect('core:check_booking')

    # -------------------------------------------------
    # VALIDASI FILE BUKTI PEMBAYARAN
    # -------------------------------------------------

    if not proof:

        messages.error(
            request,
            'Silakan unggah bukti pembayaran.'
        )

        return redirect('core:check_booking')

    extension = os.path.splitext(
        proof.name
    )[1].lower()

    allowed_extensions = [
        '.jpg',
        '.jpeg',
        '.png',
        '.pdf',
    ]

    if extension not in allowed_extensions:

        messages.error(
            request,
            'Format bukti pembayaran harus JPG, JPEG, PNG, atau PDF.'
        )

        return redirect('core:check_booking')

    if proof.size > 5 * 1024 * 1024:

        messages.error(
            request,
            'Ukuran file maksimal 5 MB.'
        )

        return redirect('core:check_booking')

    # -------------------------------------------------
    # PROSES PEMBAYARAN
    # -------------------------------------------------

    try:

        with transaction.atomic():

            booking = BookingInquiry.objects.select_for_update().get(
                pk=booking.pk
            )

            if booking.booking_status == 'cancelled':

                messages.error(
                    request,
                    'Booking sudah dibatalkan. '
                    'Pembayaran tidak dapat dilakukan.'
                )

                return redirect('core:check_booking')

            if booking.total_price <= 0:

                messages.error(
                    request,
                    'Tagihan booking belum ditentukan oleh admin. '
                    'Silakan hubungi Zhain Tour and Travel.'
                )

                return redirect('core:check_booking')

            if booking.is_fully_paid:

                messages.error(
                    request,
                    'Booking ini sudah lunas.'
                )

                return redirect('core:check_booking')

            # Jangan menerima upload baru jika masih ada
            # pembayaran yang menunggu verifikasi.

            pending_exists = booking.payments.filter(
                verification_status='pending'
            ).exists()

            if pending_exists:

                messages.error(
                    request,
                    'Masih ada pembayaran yang menunggu verifikasi admin. '
                    'Silakan tunggu hingga pembayaran sebelumnya diverifikasi.'
                )

                return redirect('core:check_booking')

            verified_dp = booking.verified_dp
            required_dp = booking.required_dp
            remaining_payment = booking.remaining_payment

            # -----------------------------------------
            # VALIDASI DP
            # -----------------------------------------

            if verified_dp < required_dp:

                if payment_type != 'dp':

                    messages.error(
                        request,
                        'Silakan selesaikan pembayaran DP seluruh peserta terlebih dahulu.'
                    )

                    return redirect('core:check_booking')

                expected_dp = required_dp - verified_dp

                if amount != expected_dp:

                    messages.error(
                        request,
                        f'Nominal DP harus sebesar Rp{expected_dp:,.0f}.'
                    )

                    return redirect('core:check_booking')

            # -----------------------------------------
            # VALIDASI SETELAH DP
            # -----------------------------------------

            else:

                if payment_type == 'dp':

                    messages.error(
                        request,
                        'DP seluruh peserta sudah terpenuhi. '
                        'Silakan pilih cicilan atau pelunasan.'
                    )

                    return redirect('core:check_booking')

                if payment_type == 'installment':

                    if amount >= remaining_payment:

                        messages.error(
                            request,
                            'Nominal cicilan harus lebih kecil dari sisa tagihan. '
                            'Jika ingin membayar seluruh sisa tagihan, '
                            'pilih pelunasan.'
                        )

                        return redirect('core:check_booking')

                elif payment_type == 'settlement':

                    if amount != remaining_payment:

                        messages.error(
                            request,
                            f'Nominal pelunasan harus sebesar '
                            f'Rp{remaining_payment:,.0f}.'
                        )

                        return redirect('core:check_booking')

            # -----------------------------------------
            # SIMPAN PEMBAYARAN
            # -----------------------------------------

            payment = PaymentRecord(
                booking=booking,
                payment_type=payment_type,
                amount=amount,
                method=method,
                proof=proof,
                verification_status='pending',
            )

            payment.full_clean()
            payment.save()

    except BookingInquiry.DoesNotExist:

        messages.error(
            request,
            'Data booking tidak ditemukan.'
        )

        return redirect('core:check_booking')

    except ValidationError as error:

        messages.error(
            request,
            ' '.join(error.messages)
        )

        return redirect('core:check_booking')

    except Exception:

        messages.error(
            request,
            'Terjadi kesalahan saat menyimpan pembayaran. '
            'Silakan coba kembali.'
        )

        return redirect('core:check_booking')

    # -------------------------------------------------
    # TAMPILKAN DETAIL BOOKING
    # -------------------------------------------------

    booking.refresh_from_db()

    payments = booking.payments.all().order_by(
        '-paid_at'
    )

    messages.success(
        request,
        'Bukti pembayaran berhasil dikirim. '
        'Pembayaran sedang menunggu verifikasi admin.'
    )

    context = {
        'booking': booking,
        'payments': payments,
        'booking_code': booking.booking_code or '',
        'application_token': str(booking.application_token),
        'phone': phone,
    }

    return render(
        request,
        'core/check_booking.html',
        context
    )


# =====================================================
# DASHBOARD ADMIN
# =====================================================

@staff_member_required(login_url='admin:login')
def admin_dashboard(request):

    bookings = BookingInquiry.objects.all()

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(
        booking_status='pending'
    ).count()

    confirmed_bookings = bookings.filter(
        booking_status='confirmed'
    ).count()

    total_revenue = (
        bookings.filter(
            payment_status__in=['dp', 'paid']
        ).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
    )

    recent_bookings = bookings[:8]

    active_packages = TourPackage.objects.filter(
        is_active=True
    ).count()

    brochure_count = Brochure.objects.filter(
        is_active=True
    ).count()

    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'active_packages': active_packages,
        'brochure_count': brochure_count,
    }

    return render(
        request,
        'admin/dashboard.html',
        context
    )

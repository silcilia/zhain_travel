
from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from django.core.exceptions import ValidationError

from .models import (
    TourPackage,
    TourDestination,
    BookingInquiry,
    BookingParticipant,
    PaymentRecord,
    Brochure,
    GalleryItem,
    Testimonial,
)

# =====================================================
# PENGATURAN TAMPILAN ADMIN
# =====================================================

admin.site.site_header = 'Zhain Tour and Travel'
admin.site.site_title = 'Zhain Admin'
admin.site.index_title = 'Manajemen Website & Pemesanan'


# =====================================================
# INLINE DATA PESERTA
# =====================================================

class BookingParticipantInline(admin.TabularInline):

    model = BookingParticipant
    extra = 0

    fields = (
        'nik',
        'full_name',
        'birth_date',
    )

    verbose_name = 'Data peserta'
    verbose_name_plural = 'Data seluruh peserta'


# =====================================================
# INLINE CATATAN PEMBAYARAN
# =====================================================

class PaymentRecordInline(admin.TabularInline):

    model = PaymentRecord
    extra = 0
    show_change_link = True

    fields = (
        'payment_label',
        'payment_type',
        'amount',
        'method',
        'reference',
        'proof',
        'verification_status',
        'paid_at',
        'verified_at',
    )

    readonly_fields = (
        'payment_label',
        'verification_status',
        'verified_at',
    )

    verbose_name = 'Catatan pembayaran'
    verbose_name_plural = 'Riwayat pembayaran'

    def has_delete_permission(self, request, obj=None):
        return True


# =====================================================
# ADMIN BOOKING
# =====================================================

@admin.register(BookingInquiry)
class BookingInquiryAdmin(admin.ModelAdmin):

    list_display = (
        'booking_code',
        'name',
        'package',
        'departure_date',
        'participants',
        'total_price',
        'amount_paid',
        'remaining_payment_display',
        'booking_status',
        'payment_status',
        'created_at',
    )

    list_filter = (
        'booking_status',
        'payment_status',
        'departure_date',
        'created_at',
    )

    search_fields = (
        'booking_code',
        'name',
        'phone',
        'email',
        'package',
    )

    readonly_fields = (
        'application_token',
        'booking_code',
        'total_price',
        'price_per_person',
        'amount_paid',
        'payment_status',
        'required_dp_display',
        'verified_dp_display',
        'remaining_after_dp_display',
        'remaining_payment_display',
        'created_at',
        'updated_at',
    )

    date_hierarchy = 'created_at'
    list_per_page = 25

    inlines = [
        BookingParticipantInline,
        PaymentRecordInline,
    ]

    fieldsets = (

        (
            'Identitas Pengajuan',
            {
                'fields': (
                    'application_token',
                    'booking_code',
                ),
                'description': (
                    'Kode booking resmi diterbitkan setelah '
                    'DP seluruh peserta terverifikasi.'
                ),
            }
        ),

        (
            'Informasi Pemesan',
            {
                'fields': (
                    'name',
                    'phone',
                    'email',
                )
            }
        ),

        (
            'Detail Perjalanan',
            {
                'fields': (
                    'package_ref',
                    'package',
                    'departure_date',
                    'participants',
                    'message',
                )
            }
        ),

        (
            'Pengaturan Harga',
            {
                'fields': (
                    'package_price_per_person',
                    'total_price',
                    'required_dp_display',
                    'verified_dp_display',
                    'remaining_after_dp_display',
                    'price_per_person',
                ),
                'description': (
                    'Harga paket ditentukan oleh admin. '
                    'DP wajib Rp150.000 per peserta dan '
                    'merupakan bagian dari harga paket.'
                ),
            }
        ),

        (
            'Ringkasan Pembayaran',
            {
                'fields': (
                    'amount_paid',
                    'remaining_payment_display',
                    'payment_status',
                ),
                'description': (
                    'Hanya pembayaran yang sudah diverifikasi '
                    'yang dihitung sebagai pembayaran.'
                ),
            }
        ),

        (
            'Status Booking',
            {
                'fields': (
                    'booking_status',
                )
            }
        ),

        (
            'Catatan Internal Admin',
            {
                'fields': (
                    'admin_notes',
                )
            }
        ),

        (
            'Riwayat',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            }
        ),
    )

    # -----------------------------------------------
    # TAMPILAN NOMINAL PEMBAYARAN
    # -----------------------------------------------

    @admin.display(description='Total DP wajib')
    def required_dp_display(self, obj):

        if not obj:
            return 'Akan dihitung setelah booking disimpan.'

        return f'Rp{obj.required_dp:,}'

    @admin.display(description='DP terverifikasi')
    def verified_dp_display(self, obj):

        if not obj:
            return '-'

        return f'Rp{obj.verified_dp:,}'

    @admin.display(description='Sisa setelah DP')
    def remaining_after_dp_display(self, obj):

        if not obj:
            return '-'

        return f'Rp{obj.remaining_after_dp:,}'

    @admin.display(description='Sisa tagihan')
    def remaining_payment_display(self, obj):

        if not obj:
            return '-'

        return f'Rp{obj.remaining_payment:,}'


# =====================================================
# ADMIN CATATAN PEMBAYARAN
# =====================================================

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):

    list_display = (
        'booking',
        'payment_label',
        'payment_type',
        'amount_display',
        'method',
        'verification_status',
        'paid_at',
        'verification_action',
    )

    list_filter = (
        'payment_type',
        'verification_status',
        'method',
        'paid_at',
    )

    search_fields = (
        'booking__booking_code',
        'booking__name',
        'reference',
    )

    readonly_fields = (
        'payment_label',
        'proof_preview',
        'verified_at',
        'created_at',
    )

    date_hierarchy = 'paid_at'
    list_per_page = 25

    actions = (
        'verify_payments',
        'reject_payments',
    )

    fieldsets = (

        (
            'Informasi Booking',
            {
                'fields': (
                    'booking',
                )
            }
        ),

        (
            'Detail Pembayaran',
            {
                'fields': (
                    'payment_label',
                    'payment_type',
                    'amount',
                    'method',
                    'reference',
                    'proof',
                    'proof_preview',
                    'paid_at',
                )
            }
        ),

        (
            'Verifikasi Pembayaran',
            {
                'fields': (
                    'verification_status',
                    'verified_at',
                ),
                'description': (
                    'Gunakan tindakan verifikasi pada daftar '
                    'pembayaran untuk menerima atau menolak pembayaran.'
                )
            }
        ),

        (
            'Riwayat',
            {
                'fields': (
                    'created_at',
                )
            }
        ),
    )

    # -----------------------------------------------
    # LABEL PEMBAYARAN
    # -----------------------------------------------

    @admin.display(description='Jenis / Urutan Pembayaran')
    def payment_label(self, obj):

        if not obj:
            return '-'

        return obj.payment_label

    @admin.display(description='Jumlah Pembayaran')
    def amount_display(self, obj):

        return f'Rp{obj.amount:,}'

    # -----------------------------------------------
    # PREVIEW BUKTI PEMBAYARAN
    # -----------------------------------------------

    @admin.display(description='Bukti Pembayaran')
    def proof_preview(self, obj):

        if obj and obj.proof:

            return format_html(
                '<a href="{}" target="_blank">'
                'Lihat bukti pembayaran'
                '</a>',
                obj.proof.url
            )

        return 'Belum ada bukti pembayaran.'

    # -----------------------------------------------
    # STATUS VERIFIKASI
    # -----------------------------------------------

    @admin.display(description='Tindakan')
    def verification_action(self, obj):

        if obj.verification_status == 'pending':
            return 'Menunggu verifikasi'

        elif obj.verification_status == 'verified':
            return 'Sudah diverifikasi'

        return 'Ditolak'

    # -----------------------------------------------
    # AKSI VERIFIKASI
    # -----------------------------------------------

    @admin.action(description='Terima / verifikasi pembayaran terpilih')
    def verify_payments(self, request, queryset):

        success_count = 0
        error_count = 0

        for payment in queryset:

            if payment.verification_status != 'pending':
                continue

            try:

                payment.verification_status = 'verified'
                payment.verified_at = timezone.now()

                # Validasi sebelum pembayaran diterima.
                payment.full_clean()

                # Simpan dan hitung ulang total pembayaran.
                payment.save()

                success_count += 1

            except ValidationError as error:

                error_count += 1

                self.message_user(
                    request,
                    (
                        f'Pembayaran {payment} tidak dapat diverifikasi: '
                        f'{error}'
                    ),
                    messages.ERROR
                )

        if success_count:

            self.message_user(
                request,
                f'{success_count} pembayaran berhasil diverifikasi.',
                messages.SUCCESS
            )

        if error_count:

            self.message_user(
                request,
                f'{error_count} pembayaran gagal diverifikasi.',
                messages.WARNING
            )

    # -----------------------------------------------
    # AKSI TOLAK PEMBAYARAN
    # -----------------------------------------------

    @admin.action(description='Tolak pembayaran terpilih')
    def reject_payments(self, request, queryset):

        count = 0

        for payment in queryset:

            if payment.verification_status == 'pending':

                payment.verification_status = 'rejected'
                payment.verified_at = None

                payment.save()

                count += 1

        self.message_user(
            request,
            f'{count} pembayaran berhasil ditolak.',
            messages.WARNING
        )


# =====================================================
# ADMIN PAKET WISATA
# =====================================================

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'destination',
        'price',
        'is_featured',
        'is_active',
        'updated_at',
    )

    list_filter = (
        'category',
        'is_active',
        'is_featured',
    )

    search_fields = (
        'name',
        'destination',
        'description',
    )

    list_editable = (
        'price',
        'is_featured',
        'is_active',
    )

    fieldsets = (

        (
            'Informasi Paket',
            {
                'fields': (
                    'name',
                    'category',
                    'destination',
                    'short_description',
                    'description',
                    'duration',
                )
            }
        ),

        (
            'Harga dan Media',
            {
                'fields': (
                    'price',
                    'image',
                    'brochure',
                )
            }
        ),

        (
            'Tampilan Website',
            {
                'fields': (
                    'is_featured',
                    'is_active',
                )
            }
        ),
    )



# =====================================================
# ADMIN DESTINASI PAKET
# =====================================================

@admin.register(TourDestination)
class TourDestinationAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'package',
        'is_active',
        'updated_at',
    )

    list_filter = (
        'package',
        'is_active',
    )

    search_fields = (
        'name',
        'short_description',
        'description',
        'package__name',
    )

    fieldsets = (
        (
            'Informasi Destinasi',
            {
                'fields': (
                    'package',
                    'name',
                    'short_description',
                    'description',
                    'facilities',
                )
            }
        ),

        (
            'Media Destinasi',
            {
                'fields': (
                    'image',
                    'brochure',
                )
            }
        ),

        (
            'Tampilan Website',
            {
                'fields': (
                    'is_active',
                )
            }
        ),
    )


# =====================================================
# ADMIN BROSUR
# =====================================================

@admin.register(Brochure)
class BrochureAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'package',
        'is_active',
        'uploaded_at',
    )

    list_filter = (
        'is_active',
        'uploaded_at',
    )

    search_fields = (
        'title',
        'package__name',
    )


# =====================================================
# ADMIN GALERI
# =====================================================

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'caption',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
        'created_at',
    )

    search_fields = (
        'title',
        'caption',
    )


# =====================================================
# ADMIN TESTIMONI
# =====================================================

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):

    list_display = (
        'customer_name',
        'trip_name',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
        'created_at',
    )

    search_fields = (
        'customer_name',
        'trip_name',
        'message',
    )

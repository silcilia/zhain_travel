
import uuid

from django.db import models, transaction
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


# =====================================================
# PAKET WISATA
# =====================================================

class TourPackage(models.Model):

    CATEGORY_CHOICES = [
        ('domestik', 'Domestik'),
        ('internasional', 'Internasional'),
        ('open_trip', 'Open Trip'),
        ('private', 'Private Tour'),
        ('custom', 'Custom Trip'),
    ]

    name = models.CharField(
        'Nama paket',
        max_length=150
    )

    destination = models.CharField(
        'Destinasi / lokasi',
        max_length=180,
        blank=True
    )

    category = models.CharField(
        'Kategori',
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='domestik'
    )

    short_description = models.CharField(
        'Deskripsi singkat',
        max_length=220,
        blank=True
    )

    description = models.TextField(
        'Deskripsi lengkap',
        blank=True
    )

    duration = models.CharField(
        'Durasi',
        max_length=80,
        blank=True,
        help_text='Contoh: 3 hari 2 malam'
    )

    price = models.PositiveBigIntegerField(
        'Harga paket per orang (Rp)',
        default=0
    )

    booking_seat_price = models.PositiveBigIntegerField(
        'DP referensi lama (Rp)',
        default=0,
        help_text='Field lama. DP aktual ditentukan oleh sistem.'
    )

    image = models.ImageField(
        'Foto paket',
        upload_to='packages/',
        blank=True,
        null=True
    )

    brochure = models.FileField(
        'Brosur (JPG/PNG/PDF)',
        upload_to='brochures/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'],
                message='Format brosur harus JPG, JPEG, PNG, atau PDF.'
            )
        ]
    )

    is_featured = models.BooleanField(
        'Tampilkan di beranda',
        default=True
    )

    is_active = models.BooleanField(
        'Aktif / tampil di website',
        default=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Paket wisata'
        verbose_name_plural = 'Paket wisata'

    def __str__(self):
        return self.name


# =====================================================
# DESTINASI DALAM PAKET WISATA
# =====================================================

class TourDestination(models.Model):

    package = models.ForeignKey(
        TourPackage,
        on_delete=models.CASCADE,
        related_name='destinations',
        verbose_name='Paket wisata'
    )

    name = models.CharField(
        'Nama destinasi',
        max_length=150
    )

    short_description = models.CharField(
        'Deskripsi singkat',
        max_length=220,
        blank=True
    )

    description = models.TextField(
        'Deskripsi lengkap',
        blank=True
    )

    facilities = models.TextField(
        'Fasilitas paket',
        blank=True,
        help_text='Pisahkan setiap fasilitas dengan baris baru.'
    )

    image = models.ImageField(
        'Foto destinasi',
        upload_to='destinations/',
        blank=True,
        null=True
    )

    brochure = models.FileField(
        'Brosur destinasi (PDF/JPG/PNG)',
        upload_to='brochures/destinations/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'],
                message='Format brosur harus JPG, JPEG, PNG, atau PDF.'
            )
        ]
    )

    is_active = models.BooleanField(
        'Tampilkan di website',
        default=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Destinasi paket'
        verbose_name_plural = 'Destinasi paket'

    def __str__(self):
        return f'{self.package.name} - {self.name}'


# =====================================================
# BOOKING CUSTOMER
# =====================================================

class BookingInquiry(models.Model):

    # DP wajib per peserta.
    DP_PER_PERSON = 150000

    BOOKING_STATUS = [
        ('pending', 'Menunggu konfirmasi'),
        ('confirmed', 'Dikonfirmasi'),
        ('ongoing', 'Sedang berlangsung'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]

    PAYMENT_STATUS = [
        ('unpaid', 'Belum dibayar'),
        ('dp', 'Sudah DP'),
        ('paid', 'Lunas'),
        ('refunded', 'Dikembalikan'),
    ]

    application_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    booking_code = models.CharField(
        'Kode booking',
        max_length=24,
        unique=True,
        blank=True,
        null=True
    )

    # INFORMASI PEMESAN

    name = models.CharField(
        'Nama pemesan',
        max_length=100
    )

    phone = models.CharField(
        'Nomor WhatsApp',
        max_length=30
    )

    email = models.EmailField(
        'Email',
        blank=True
    )

    # PAKET PERJALANAN

    package_ref = models.ForeignKey(
        TourPackage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        verbose_name='Paket terkait'
    )

    destination_ref = models.ForeignKey(
        TourDestination,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        verbose_name='Destinasi terkait'
    )

    package = models.CharField(
        'Nama paket saat booking',
        max_length=150,
        blank=True
    )

    departure_date = models.DateField(
        'Tanggal keberangkatan',
        null=True,
        blank=True
    )

    participants = models.PositiveSmallIntegerField(
        'Jumlah peserta',
        default=1
    )

    # HARGA PAKET

    package_price_per_person = models.PositiveBigIntegerField(
        'Harga paket per orang (Rp)',
        default=0,
        help_text='Harga penuh satu peserta. Diisi admin.'
    )

    total_price = models.PositiveBigIntegerField(
        'Total harga paket (Rp)',
        default=0,
        help_text='Harga paket per orang dikali jumlah peserta.'
    )

    # FIELD DP KOMPATIBILITAS

    price_per_person = models.PositiveBigIntegerField(
        'DP per peserta (Rp)',
        default=150000,
        editable=False
    )

    booking_seat_price = models.PositiveBigIntegerField(
        'DP lama (kompatibilitas data)',
        default=0,
        editable=False
    )

    # TOTAL PEMBAYARAN

    amount_paid = models.PositiveBigIntegerField(
        'Total pembayaran terverifikasi (Rp)',
        default=0,
        editable=False
    )

    payment_status = models.CharField(
        'Status pembayaran',
        max_length=20,
        choices=PAYMENT_STATUS,
        default='unpaid'
    )

    # STATUS BOOKING

    booking_status = models.CharField(
        'Status booking',
        max_length=20,
        choices=BOOKING_STATUS,
        default='pending'
    )

    message = models.TextField(
        'Catatan / permintaan khusus',
        blank=True
    )

    admin_notes = models.TextField(
        'Catatan internal admin',
        blank=True
    )

    created_at = models.DateTimeField(
        'Tanggal pemesanan',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        'Terakhir diperbarui',
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Data booking'

    def __str__(self):
        return f'{self.booking_code or "Pengajuan baru"} - {self.name}'

    # =================================================
    # PERHITUNGAN HARGA DAN PEMBAYARAN
    # =================================================

    @property
    def total_booking_seat(self):
        """Total DP wajib seluruh peserta."""
        return self.DP_PER_PERSON * self.participants

    @property
    def required_dp(self):
        """Jumlah DP yang harus dibayar."""
        return self.total_booking_seat

    @property
    def verified_dp(self):
        """Total pembayaran DP yang sudah diverifikasi."""
        return self.payments.filter(
            payment_type='dp',
            verification_status='verified'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def remaining_payment(self):
        """Sisa tagihan setelah pembayaran terverifikasi."""
        return max(self.total_price - self.amount_paid, 0)

    @property
    def remaining_after_dp(self):
        """Sisa tagihan setelah DP terverifikasi."""
        return max(self.total_price - self.verified_dp, 0)

    @property
    def is_dp_paid(self):
        """Memeriksa apakah DP seluruh peserta sudah terpenuhi."""
        return self.verified_dp >= self.required_dp

    @property
    def is_fully_paid(self):
        """Memeriksa apakah seluruh tagihan sudah lunas."""
        return (
            self.total_price > 0
            and self.amount_paid >= self.total_price
        )

    def update_payment_status(self):
        """Menentukan status pembayaran secara otomatis."""

        if self.payment_status == 'refunded':
            return

        if self.amount_paid <= 0:
            self.payment_status = 'unpaid'

        elif self.is_fully_paid:
            self.payment_status = 'paid'

        elif self.is_dp_paid:
            self.payment_status = 'dp'

        else:
            self.payment_status = 'unpaid'

    def issue_booking_code(self):
        """
        Kode booking diterbitkan setelah
        DP seluruh peserta terverifikasi.
        """

        if self.booking_code or not self.pk:
            return

        if not self.is_dp_paid:
            return

        new_code = (
            f'ZHN-{timezone.localdate():%Y%m}-{self.pk:06d}'
        )

        updated = type(self).objects.filter(
            pk=self.pk,
            booking_code__isnull=True
        ).update(
            booking_code=new_code
        )

        if updated:
            self.booking_code = new_code

    def save(self, *args, **kwargs):

        creating = self.pk is None

        if creating and self.package_ref and not self.package:
            self.package = self.package_ref.name

        # Menghitung harga seluruh peserta.
        self.total_price = (
            self.package_price_per_person * self.participants
        )

        # DP ditetapkan oleh sistem.
        self.price_per_person = self.DP_PER_PERSON
        self.booking_seat_price = self.DP_PER_PERSON

        if not creating:
            self.update_payment_status()

        super().save(*args, **kwargs)


# =====================================================
# DATA PESERTA BOOKING
# =====================================================

class BookingParticipant(models.Model):

    booking = models.ForeignKey(
        BookingInquiry,
        on_delete=models.CASCADE,
        related_name='participant_details',
        verbose_name='Booking'
    )

    nik = models.CharField(
        'NIK',
        max_length=16
    )

    full_name = models.CharField(
        'Nama lengkap peserta',
        max_length=150
    )

    birth_date = models.DateField(
        'Tanggal lahir'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Data peserta'
        verbose_name_plural = 'Data peserta'

    def __str__(self):
        return self.full_name


# =====================================================
# CATATAN PEMBAYARAN
# =====================================================

class PaymentRecord(models.Model):

    PAYMENT_TYPE_CHOICES = [
        ('dp', 'DP'),
        ('installment', 'Cicilan'),
        ('settlement', 'Pelunasan'),
    ]

    METHOD_CHOICES = [
        ('transfer', 'Transfer bank'),
        ('cash', 'Tunai'),
        ('qris', 'QRIS'),
        ('other', 'Lainnya'),
    ]

    VERIFICATION_CHOICES = [
        ('pending', 'Menunggu verifikasi'),
        ('verified', 'Terverifikasi'),
        ('rejected', 'Ditolak'),
    ]

    booking = models.ForeignKey(
        BookingInquiry,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Booking'
    )

    payment_type = models.CharField(
        'Jenis pembayaran',
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        default='installment'
    )

    amount = models.PositiveBigIntegerField(
        'Jumlah pembayaran (Rp)'
    )

    method = models.CharField(
        'Metode pembayaran',
        max_length=20,
        choices=METHOD_CHOICES,
        default='transfer'
    )

    reference = models.CharField(
        'Nomor referensi / catatan',
        max_length=120,
        blank=True
    )

    proof = models.FileField(
        'Bukti pembayaran',
        upload_to='payment_proofs/',
        blank=True,
        null=True
    )

    verification_status = models.CharField(
        'Status verifikasi',
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default='pending',
        help_text='Pembayaran harus diverifikasi admin sebelum dihitung.'
    )

    verified_at = models.DateTimeField(
        'Waktu verifikasi',
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        'Waktu pembayaran',
        default=timezone.now
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['paid_at', 'created_at']
        verbose_name = 'Catatan pembayaran'
        verbose_name_plural = 'Catatan pembayaran'

    def __str__(self):
        return (
            f'{self.booking.booking_code or "Pengajuan"} '
            f'- {self.get_payment_type_display()} '
            f'- Rp{self.amount:,}'
        )

    @property
    def payment_label(self):
        """Menampilkan label riwayat pembayaran."""

        if self.payment_type == 'dp':
            return 'DP'

        if self.payment_type == 'settlement':
            return 'Pelunasan'

        previous_count = PaymentRecord.objects.filter(
            booking_id=self.booking_id,
            payment_type='installment',
            paid_at__lt=self.paid_at
        ).count()

        return f'Pembayaran {previous_count + 1}'

    def clean(self):

        super().clean()

        if not self.booking_id:
            return

        booking = self.booking

        if self.amount is None or self.amount <= 0:
            raise ValidationError({
                'amount': 'Jumlah pembayaran harus lebih dari Rp0.'
            })

        # Mengambil transaksi yang sudah diverifikasi.
        verified_payments = booking.payments.filter(
            verification_status='verified'
        )

        if self.pk:
            verified_payments = verified_payments.exclude(
                pk=self.pk
            )

        # Menghitung total pembayaran terverifikasi.
        already_paid = verified_payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        remaining = max(
            booking.total_price - already_paid,
            0
        )

        if remaining <= 0:
            raise ValidationError(
                'Booking sudah lunas. Tidak dapat menerima pembayaran baru.'
            )

        if self.amount > remaining:
            raise ValidationError({
                'amount': (
                    f'Pembayaran melebihi sisa tagihan. '
                    f'Sisa tagihan Rp{remaining:,}.'
                )
            })

        # Menghitung DP yang sudah diverifikasi.
        existing_dp = verified_payments.filter(
            payment_type='dp'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        required_dp = booking.required_dp
        dp_remaining = max(required_dp - existing_dp, 0)

        # VALIDASI DP
        if self.payment_type == 'dp':

            if dp_remaining <= 0:
                raise ValidationError({
                    'payment_type': 'DP sudah terpenuhi.'
                })

            if self.amount != dp_remaining:
                raise ValidationError({
                    'amount': (
                        f'Jumlah DP harus sebesar Rp{dp_remaining:,}.'
                    )
                })

        # VALIDASI CICILAN
        elif self.payment_type == 'installment':

            if existing_dp < required_dp:
                raise ValidationError({
                    'payment_type': (
                        'DP seluruh peserta harus terverifikasi '
                        'sebelum melakukan cicilan.'
                    )
                })

            if self.amount >= remaining:
                raise ValidationError({
                    'payment_type': (
                        'Untuk membayar seluruh sisa tagihan, '
                        'silakan pilih jenis pembayaran pelunasan.'
                    )
                })

        # VALIDASI PELUNASAN
        elif self.payment_type == 'settlement':

            if existing_dp < required_dp:
                raise ValidationError({
                    'payment_type': (
                        'DP seluruh peserta harus terverifikasi '
                        'sebelum melakukan pelunasan.'
                    )
                })

            if self.amount != remaining:
                raise ValidationError({
                    'amount': (
                        f'Jumlah pelunasan harus sebesar '
                        f'Rp{remaining:,}.'
                    )
                })

    def save(self, *args, **kwargs):

        old_booking = None

        if self.pk:
            old_record = (
                PaymentRecord.objects
                .filter(pk=self.pk)
                .only('booking_id')
                .first()
            )

            if (
                old_record
                and old_record.booking_id != self.booking_id
            ):
                old_booking = BookingInquiry.objects.filter(
                    pk=old_record.booking_id
                ).first()

        # Mengatur waktu verifikasi.
        if self.verification_status == 'verified':
            if not self.verified_at:
                self.verified_at = timezone.now()
        else:
            self.verified_at = None

        super().save(*args, **kwargs)

        self.sync_booking_totals(self.booking)

        if old_booking:
            self.sync_booking_totals(old_booking)

    def delete(self, *args, **kwargs):

        booking = self.booking

        result = super().delete(*args, **kwargs)

        self.sync_booking_totals(booking)

        return result

    @staticmethod
    def sync_booking_totals(booking):
        """
        Menghitung ulang total pembayaran.
        Hanya transaksi terverifikasi yang dihitung.
        """

        total_paid = booking.payments.filter(
            verification_status='verified'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        booking.amount_paid = total_paid

        booking.update_payment_status()

        booking.save(
            update_fields=[
                'amount_paid',
                'payment_status',
                'updated_at',
            ]
        )

        booking.refresh_from_db()

        # Terbitkan kode booking jika DP sudah terpenuhi.
        booking.issue_booking_code()


# =====================================================
# BROSUR
# =====================================================

class Brochure(models.Model):

    title = models.CharField(
        'Judul brosur',
        max_length=150
    )

    package = models.ForeignKey(
        TourPackage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brochures',
        verbose_name='Paket terkait'
    )

    file = models.FileField(
        'File brosur (PDF/JPG/PNG)',
        upload_to='brochures/library/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'],
                message='Format file harus PDF, JPG, JPEG, atau PNG.'
            )
        ]
    )

    is_active = models.BooleanField(
        'Tampilkan di website',
        default=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Brosur'
        verbose_name_plural = 'Brosur'

    def __str__(self):
        return self.title


# =====================================================
# GALERI
# =====================================================

class GalleryItem(models.Model):

    title = models.CharField(
        'Judul foto',
        max_length=120
    )

    image = models.ImageField(
        'Foto',
        upload_to='gallery/'
    )

    caption = models.CharField(
        'Keterangan',
        max_length=220,
        blank=True
    )

    is_active = models.BooleanField(
        'Tampilkan di website',
        default=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Foto galeri'
        verbose_name_plural = 'Galeri foto'

    def __str__(self):
        return self.title


# =====================================================
# TESTIMONI
# =====================================================

class Testimonial(models.Model):

    customer_name = models.CharField(
        'Nama pelanggan',
        max_length=100
    )

    trip_name = models.CharField(
        'Paket / perjalanan',
        max_length=150,
        blank=True
    )

    message = models.TextField('Testimoni')

    is_active = models.BooleanField(
        'Tampilkan di website',
        default=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Testimoni'
        verbose_name_plural = 'Testimoni'

    def __str__(self):
        return f'{self.customer_name} - {self.trip_name}'

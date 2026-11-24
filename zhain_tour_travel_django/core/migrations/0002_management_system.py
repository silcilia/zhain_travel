import django.utils.timezone
from django.db import migrations, models
import django.db.models.deletion


def populate_existing_booking_codes(apps, schema_editor):
    Booking = apps.get_model('core', 'BookingInquiry')
    for booking in Booking.objects.filter(booking_code='').order_by('id'):
        booking.booking_code = f'ZHN-LEGACY-{booking.pk:06d}'
        booking.save(update_fields=['booking_code'])


def seed_packages(apps, schema_editor):
    Package = apps.get_model('core', 'TourPackage')
    rows = [
        ('Palembang – Pahawang', 'Sumatera Selatan & Lampung', 'domestik'),
        ('Palembang – Wayang Pahawang', 'Lampung', 'domestik'),
        ('Bangka', 'Kepulauan Bangka Belitung', 'domestik'),
        ('Bali – Lombok', 'Bali & Nusa Tenggara', 'domestik'),
        ('Bandung', 'Jawa Barat', 'domestik'),
        ('Bromo', 'Jawa Timur', 'domestik'),
        ('Yogyakarta', 'Daerah Istimewa Yogyakarta', 'domestik'),
        ('Malaysia', 'Kuala Lumpur & sekitarnya', 'internasional'),
        ('Singapore', 'Singapore', 'internasional'),
        ('Thailand – Bangkok', 'Bangkok, Thailand', 'internasional'),
    ]
    for name, destination, category in rows:
        Package.objects.get_or_create(name=name, defaults={'destination': destination, 'category': category, 'is_active': True, 'is_featured': True})


class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='TourPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Nama paket')),
                ('destination', models.CharField(blank=True, max_length=180, verbose_name='Destinasi / lokasi')),
                ('category', models.CharField(choices=[('domestik', 'Domestik'), ('internasional', 'Internasional'), ('open_trip', 'Open Trip'), ('private', 'Private Tour'), ('custom', 'Custom Trip')], default='domestik', max_length=30, verbose_name='Kategori')),
                ('short_description', models.CharField(blank=True, max_length=220, verbose_name='Deskripsi singkat')),
                ('description', models.TextField(blank=True, verbose_name='Deskripsi lengkap')),
                ('duration', models.CharField(blank=True, max_length=80, verbose_name='Durasi')),
                ('price', models.PositiveBigIntegerField(default=0, verbose_name='Harga per orang (Rp)')),
                ('image', models.ImageField(blank=True, null=True, upload_to='packages/', verbose_name='Foto paket')),
                ('brochure', models.FileField(blank=True, null=True, upload_to='brochures/', verbose_name='Brosur PDF')),
                ('is_featured', models.BooleanField(default=True, verbose_name='Tampilkan di beranda')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif / tampil di website')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Paket wisata', 'verbose_name_plural': 'Paket wisata', 'ordering': ['name']},
        ),
        migrations.AddField(model_name='bookinginquiry', name='booking_code', field=models.CharField(blank=True, max_length=24, unique=True, verbose_name='Kode booking')),
        migrations.RunPython(populate_existing_booking_codes, migrations.RunPython.noop),
        migrations.AlterField(model_name='bookinginquiry', name='booking_code', field=models.CharField(blank=True, max_length=24, unique=True, verbose_name='Kode booking')),
        migrations.AddField(model_name='bookinginquiry', name='email', field=models.EmailField(blank=True, max_length=254, verbose_name='Email')),
        migrations.AddField(model_name='bookinginquiry', name='departure_date', field=models.DateField(blank=True, null=True, verbose_name='Tanggal keberangkatan')),
        migrations.AddField(model_name='bookinginquiry', name='participants', field=models.PositiveSmallIntegerField(default=1, verbose_name='Jumlah peserta')),
        migrations.AddField(model_name='bookinginquiry', name='price_per_person', field=models.PositiveBigIntegerField(default=0, verbose_name='Harga per orang saat booking (Rp)')),
        migrations.AddField(model_name='bookinginquiry', name='total_price', field=models.PositiveBigIntegerField(default=0, verbose_name='Total harga saat booking (Rp)')),
        migrations.AddField(model_name='bookinginquiry', name='amount_paid', field=models.PositiveBigIntegerField(default=0, verbose_name='Jumlah sudah dibayar (Rp)')),
        migrations.AddField(model_name='bookinginquiry', name='payment_status', field=models.CharField(choices=[('unpaid', 'Belum dibayar'), ('dp', 'Sudah DP'), ('paid', 'Lunas'), ('refunded', 'Dikembalikan')], default='unpaid', max_length=20, verbose_name='Status pembayaran')),
        migrations.AddField(model_name='bookinginquiry', name='booking_status', field=models.CharField(choices=[('pending', 'Menunggu konfirmasi'), ('confirmed', 'Dikonfirmasi'), ('ongoing', 'Sedang berlangsung'), ('completed', 'Selesai'), ('cancelled', 'Dibatalkan')], default='pending', max_length=20, verbose_name='Status booking')),
        migrations.AddField(model_name='bookinginquiry', name='admin_notes', field=models.TextField(blank=True, verbose_name='Catatan internal admin')),
        migrations.AddField(model_name='bookinginquiry', name='updated_at', field=models.DateTimeField(auto_now=True, verbose_name='Terakhir diperbarui')),
        migrations.AlterField(model_name='bookinginquiry', name='package', field=models.CharField(blank=True, max_length=150, verbose_name='Nama paket saat booking')),
        migrations.AlterField(model_name='bookinginquiry', name='name', field=models.CharField(max_length=100, verbose_name='Nama pemesan')),
        migrations.AlterField(model_name='bookinginquiry', name='phone', field=models.CharField(max_length=30, verbose_name='Nomor WhatsApp')),
        migrations.AlterField(model_name='bookinginquiry', name='message', field=models.TextField(blank=True, verbose_name='Catatan / permintaan khusus')),
        migrations.AlterField(model_name='bookinginquiry', name='created_at', field=models.DateTimeField(auto_now_add=True, verbose_name='Tanggal pemesanan')),
        migrations.AlterModelOptions(name='bookinginquiry', options={'ordering': ['-created_at'], 'verbose_name': 'Booking', 'verbose_name_plural': 'Data booking'}),
        migrations.AddField(model_name='bookinginquiry', name='package_ref', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bookings', to='core.tourpackage', verbose_name='Paket terkait')),
        migrations.CreateModel(
            name='PaymentRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveBigIntegerField(verbose_name='Jumlah pembayaran (Rp)')),
                ('method', models.CharField(choices=[('transfer', 'Transfer bank'), ('cash', 'Tunai'), ('qris', 'QRIS'), ('other', 'Lainnya')], default='transfer', max_length=20, verbose_name='Metode pembayaran')),
                ('reference', models.CharField(blank=True, max_length=120, verbose_name='Nomor referensi / catatan')),
                ('proof', models.FileField(blank=True, null=True, upload_to='payment_proofs/', verbose_name='Bukti pembayaran')),
                ('paid_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Waktu pembayaran')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='core.bookinginquiry', verbose_name='Booking')),
            ],
            options={'verbose_name': 'Catatan pembayaran', 'verbose_name_plural': 'Catatan pembayaran', 'ordering': ['-paid_at']},
        ),
        migrations.CreateModel(
            name='Brochure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Judul brosur')),
                ('file', models.FileField(upload_to='brochures/library/', verbose_name='File brosur (PDF)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Tampilkan di website')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='brochures', to='core.tourpackage', verbose_name='Paket terkait')),
            ],
            options={'verbose_name': 'Brosur', 'verbose_name_plural': 'Brosur', 'ordering': ['-uploaded_at']},
        ),
        migrations.CreateModel(
            name='GalleryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='Judul foto')),
                ('image', models.ImageField(upload_to='gallery/', verbose_name='Foto')),
                ('caption', models.CharField(blank=True, max_length=220, verbose_name='Keterangan')),
                ('is_active', models.BooleanField(default=True, verbose_name='Tampilkan di website')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Foto galeri', 'verbose_name_plural': 'Galeri foto', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=100, verbose_name='Nama pelanggan')),
                ('trip_name', models.CharField(blank=True, max_length=150, verbose_name='Paket / perjalanan')),
                ('message', models.TextField(verbose_name='Testimoni')),
                ('is_active', models.BooleanField(default=True, verbose_name='Tampilkan di website')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Testimoni', 'verbose_name_plural': 'Testimoni', 'ordering': ['-created_at']},
        ),
        migrations.RunPython(seed_packages, migrations.RunPython.noop),
    ]

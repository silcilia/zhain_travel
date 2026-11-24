# Zhain Tour and Travel — Django + Admin Management

Website company profile, katalog paket dinamis, form booking, pencatatan pembayaran, brosur, galeri, testimoni, dan dashboard admin.

## Menjalankan di Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Website: http://127.0.0.1:8000/
Dashboard admin ringkas: http://127.0.0.1:8000/panel/
Kelola data lengkap: http://127.0.0.1:8000/admin/

## Menu admin

- **Data booking**: kode booking, customer, kontak, paket, tanggal berangkat, peserta, snapshot harga, status booking, status pembayaran, catatan admin.
- **Paket wisata**: tambah/edit/hapus paket, kategori, destinasi, deskripsi, durasi, harga, foto, brosur, status tampil.
- **Catatan pembayaran**: catat DP/pelunasan, metode, referensi, bukti pembayaran. Total pembayaran dan status pembayaran booking dihitung dari catatan pembayaran.
- **Brosur**: upload PDF, kaitkan ke paket, atur tampil/tidak di website.
- **Galeri foto**: upload dokumentasi dan atur tampil/tidak.
- **Testimoni**: masukkan testimoni asli pelanggan dan atur tampil/tidak.

Migration awal akan membuat 10 paket destinasi awal. Harga awal Rp0 agar admin dapat mengisi harga yang benar sebelum menerima pesanan.

## Alur booking

1. Customer mengisi form di website: nama, WhatsApp, email (opsional), paket, tanggal, jumlah peserta, catatan.
2. Sistem menyimpan booking dan membuat kode unik `ZHN-YYYYMM-000001`.
3. Harga dan nama paket disimpan sebagai snapshot ketika customer mengirim form; perubahan harga paket di masa depan tidak mengubah transaksi lama.
4. Customer diarahkan ke WhatsApp dengan ringkasan booking dan kode booking.
5. Admin login, memeriksa booking, mengubah status, dan menambahkan catatan pembayaran melalui bagian inline di detail booking atau menu Catatan Pembayaran.

## Konfigurasi wajib sebelum online

1. Atur `WHATSAPP_NUMBER` di environment variable menjadi nomor resmi format internasional tanpa `+`, misalnya `62812...`.
2. Ganti `SECRET_KEY`, set `DEBUG=False`, dan isi `ALLOWED_HOSTS` sesuai domain. Jangan gunakan SECRET_KEY development untuk produksi.
3. Konfigurasikan HTTPS, backup database, dan penyimpanan `media/` secara rutin.
4. Buat akun admin/staff masing-masing orang; jangan berbagi satu akun. Berikan permission sesuai tugas.
5. Isi harga, itinerary, fasilitas, foto, dan brosur resmi. Paket awal sengaja memiliki harga Rp0 sebagai placeholder.
6. Form saat ini adalah permintaan booking/konfirmasi, bukan pembayaran online otomatis. Admin tetap memverifikasi transfer secara manual sebelum menandai pembayaran.

## Catatan

SQLite dipakai untuk development awal. Untuk website live dengan beberapa admin dan transaksi berjalan, disarankan pindah ke PostgreSQL/MySQL, aktifkan HTTPS, backup terjadwal, dan gunakan server media yang persisten.

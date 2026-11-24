
from datetime import datetime
from io import BytesIO

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from .models import BookingInquiry, PaymentRecord


# BANTUAN FORMAT EXCEL

def format_header(ws, row_number):
    """Memberikan format pada baris judul kolom."""
    for cell in ws[row_number]:
        if cell.value is not None:
            cell.font = Font(
                name="Arial",
                size=10,
                bold=True,
                color="FFFFFF"
            )
            cell.fill = PatternFill(
                fill_type="solid",
                fgColor="198754"
            )
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True
            )

    ws.row_dimensions[row_number].height = 30


def format_title(ws, title, subtitle, total_columns):
    """Membuat judul dan subjudul laporan."""
    ws.merge_cells(
        start_row=1,
        start_column=1,
        end_row=1,
        end_column=total_columns
    )

    title_cell = ws.cell(row=1, column=1, value=title)
    title_cell.font = Font(
        name="Arial",
        size=16,
        bold=True,
        color="FFFFFF"
    )
    title_cell.fill = PatternFill(
        fill_type="solid",
        fgColor="198754"
    )
    title_cell.alignment = Alignment(
        horizontal="center",
        vertical="center"
    )

    ws.row_dimensions[1].height = 32

    ws.merge_cells(
        start_row=2,
        start_column=1,
        end_row=2,
        end_column=total_columns
    )

    subtitle_cell = ws.cell(row=2, column=1, value=subtitle)
    subtitle_cell.font = Font(
        name="Arial",
        size=10,
        italic=True,
        color="666666"
    )
    subtitle_cell.alignment = Alignment(
        horizontal="center",
        vertical="center"
    )


def format_sheet(ws):
    """Mengatur tampilan umum worksheet."""
    thin_border = Border(
        bottom=Side(
            style="thin",
            color="DDDDDD"
        )
    )

    for row in ws.iter_rows():
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(
                vertical="center",
                wrap_text=True
            )

    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A5"


def adjust_column_width(ws):
    """Mengatur lebar kolom berdasarkan panjang isi."""
    for column_cells in ws.columns:
        max_length = 0
        column_letter = get_column_letter(
            column_cells[0].column
        )

        for cell in column_cells:
            if cell.value is not None:
                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        ws.column_dimensions[column_letter].width = min(
            max(max_length + 3, 12),
            40
        )


def get_month_name(month):
    """Mengubah angka bulan menjadi nama bulan Indonesia."""
    month_names = [
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember"
    ]

    return month_names[month - 1]


def get_period(request):
    """Mengambil dan memvalidasi bulan serta tahun dari URL."""
    current_date = timezone.localdate()

    try:
        month = int(
            request.GET.get("month", current_date.month)
        )

        year = int(
            request.GET.get("year", current_date.year)
        )

        if not 1 <= month <= 12:
            raise ValueError

        if not 2000 <= year <= 2100:
            raise ValueError

        return month, year

    except (ValueError, TypeError):
        return None, None

# EXPORT REKAP EXCEL BULANAN

@staff_member_required
def export_rekap_excel(request):

    # Mengambil periode laporan

    month, year = get_period(request)

    if month is None or year is None:
        return HttpResponse(
            "Bulan atau tahun yang dipilih tidak valid.",
            status=400
        )

    month_label = get_month_name(month)
    period_label = f"{month_label} {year}"

    # Menentukan batas tanggal laporan

    start_date = datetime(year, month, 1)

    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    current_timezone = timezone.get_current_timezone()

    start_datetime = timezone.make_aware(
        start_date,
        current_timezone
    )

    end_datetime = timezone.make_aware(
        end_date,
        current_timezone
    )


    # Mengambil data booking berdasarkan created_at
    

    bookings = BookingInquiry.objects.filter(
        created_at__gte=start_datetime,
        created_at__lt=end_datetime
    ).select_related(
        "package_ref"
    ).order_by(
        "created_at"
    )

    total_bookings = bookings.count()

    total_participants = bookings.aggregate(
        total=Sum("participants")
    )["total"] or 0

    total_booking_value = bookings.aggregate(
        total=Sum("total_price")
    )["total"] or 0

    # Mengambil data pembayaran berdasarkan paid_at

    payments = PaymentRecord.objects.filter(
        paid_at__gte=start_datetime,
        paid_at__lt=end_datetime
    ).select_related(
        "booking"
    ).order_by(
        "paid_at"
    )

    total_transactions = payments.count()

    total_payment = payments.aggregate(
        total=Sum("amount")
    )["total"] or 0

    # Membuat workbook

    workbook = Workbook()

    # SHEET 1: RINGKASAN

    ws_summary = workbook.active
    ws_summary.title = "Ringkasan"

    format_title(
        ws_summary,
        "LAPORAN ZHAIN TOUR AND TRAVEL",
        f"Periode Laporan: {period_label}",
        2
    )

    # Informasi booking
    ws_summary.append(["", ""])
    ws_summary.append([
        "INFORMASI BOOKING",
        "JUMLAH"
    ])

    ws_summary.append([
        "Total Booking",
        total_bookings
    ])

    ws_summary.append([
        "Total Peserta",
        total_participants
    ])

    ws_summary.append([
        "Total Nilai Booking",
        total_booking_value
    ])

    # Informasi pembayaran
    ws_summary.append(["", ""])
    ws_summary.append([
        "INFORMASI PEMBAYARAN",
        "JUMLAH"
    ])

    ws_summary.append([
        "Total Transaksi Pembayaran",
        total_transactions
    ])

    ws_summary.append([
        "Total Pembayaran Masuk",
        total_payment
    ])

    # Rekap status booking
    ws_summary.append(["", ""])
    booking_status_header = ws_summary.max_row + 1

    ws_summary.append([
        "REKAP STATUS BOOKING",
        "JUMLAH"
    ])

    for status_code, status_label in BookingInquiry.BOOKING_STATUS:

        count = bookings.filter(
            booking_status=status_code
        ).count()

        ws_summary.append([
            status_label,
            count
        ])

    # Rekap status pembayaran
    ws_summary.append(["", ""])
    payment_status_header = ws_summary.max_row + 1

    ws_summary.append([
        "REKAP STATUS PEMBAYARAN",
        "JUMLAH"
    ])

    for status_code, status_label in BookingInquiry.PAYMENT_STATUS:

        count = bookings.filter(
            payment_status=status_code
        ).count()

        ws_summary.append([
            status_label,
            count
        ])

    # Format header ringkasan
    format_header(ws_summary, 4)
    format_header(ws_summary, 9)
    format_header(ws_summary, booking_status_header)
    format_header(ws_summary, payment_status_header)

    # Format mata uang
    ws_summary["B7"].number_format = '"Rp"#,##0'
    ws_summary["B11"].number_format = '"Rp"#,##0'

    format_sheet(ws_summary)
    adjust_column_width(ws_summary)

    # SHEET 2: DETAIL BOOKING

    ws_booking = workbook.create_sheet(
        title="Detail Booking"
    )

    format_title(
        ws_booking,
        "DETAIL BOOKING PELANGGAN",
        f"Periode Booking: {period_label}",
        11
    )

    booking_headers = [
        "No.",
        "Tanggal Booking",
        "Kode Booking",
        "Nama Pelanggan",
        "Nomor WhatsApp",
        "Email",
        "Paket Wisata",
        "Tanggal Keberangkatan",
        "Jumlah Peserta",
        "Total Harga",
        "Status Booking"
    ]

    ws_booking.append([])
    ws_booking.append(booking_headers)

    for number, booking in enumerate(bookings, start=1):

        created_at = timezone.localtime(
            booking.created_at
        )

        departure_date = (
            booking.departure_date.strftime("%d-%m-%Y")
            if booking.departure_date
            else "-"
        )

        ws_booking.append([
            number,
            created_at.strftime("%d-%m-%Y %H:%M"),
            booking.booking_code,
            booking.name,
            booking.phone,
            booking.email or "-",
            booking.package or "-",
            departure_date,
            booking.participants,
            booking.total_price,
            booking.get_booking_status_display()
        ])

    format_header(ws_booking, 4)
    format_sheet(ws_booking)
    adjust_column_width(ws_booking)

    # Format kolom total harga
    for row_number in range(5, ws_booking.max_row + 1):
        ws_booking.cell(
            row=row_number,
            column=10
        ).number_format = '"Rp"#,##0'

    # SHEET 3: DETAIL PEMBAYARAN

    ws_payment = workbook.create_sheet(
        title="Detail Pembayaran"
    )

    format_title(
        ws_payment,
        "DETAIL TRANSAKSI PEMBAYARAN",
        f"Periode Pembayaran: {period_label}",
        7
    )

    payment_headers = [
        "No.",
        "Tanggal Pembayaran",
        "Kode Booking",
        "Nama Pelanggan",
        "Metode Pembayaran",
        "Referensi Transaksi",
        "Nominal Pembayaran"
    ]

    ws_payment.append([])
    ws_payment.append(payment_headers)

    for number, payment in enumerate(payments, start=1):

        paid_at = timezone.localtime(
            payment.paid_at
        )

        ws_payment.append([
            number,
            paid_at.strftime("%d-%m-%Y %H:%M"),
            payment.booking.booking_code,
            payment.booking.name,
            payment.get_method_display(),
            payment.reference or "-",
            payment.amount
        ])

    format_header(ws_payment, 4)
    format_sheet(ws_payment)
    adjust_column_width(ws_payment)

    # Format kolom nominal pembayaran
    for row_number in range(5, ws_payment.max_row + 1):
        ws_payment.cell(
            row=row_number,
            column=7
        ).number_format = '"Rp"#,##0'

    # MENYIAPKAN FILE EXCEL UNTUK DIUNDUH

    output = BytesIO()

    workbook.save(output)
    output.seek(0)

    filename = (
        f"Rekap_Zhain_Tour_Travel_"
        f"{year}_{month:02d}.xlsx"
    )

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    return response

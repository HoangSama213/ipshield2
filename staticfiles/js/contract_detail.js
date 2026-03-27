function showFullInfo(time, date) {
    alert("📑 CHI TIẾT XUẤT HÓA ĐƠN\n--------------------------\n✅ Trạng thái: Đã xuất hóa đơn đỏ\n🕒 Giờ xác nhận: " + time + "\n📅 Ngày xác nhận: " + date);
}
function exportBill(id) {
    if(confirm('Xuất hóa đơn đỏ?')) {
        fetch(`/export-bill/${id}/`, {
            method: 'POST',
            headers: {'X-CSRFToken': '{{ csrf_token }}'}
        })
        .then(r => r.json())
        .then(data => {
            if(data.success) {
                alert('Đã xuất hóa đơn!');
                location.reload();
            }
        });
    }
}
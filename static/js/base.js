function updateClock() {
    const now = new Date();

    // Mảng thứ trong tuần
    const days = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
    const dayName = days[now.getDay()];

    // Lấy ngày, tháng, năm
    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const year = now.getFullYear();

    // Lấy giờ, phút, giây
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    // Tạo chuỗi hiển thị
    const dateTimeString = `${dayName}, ${day}/${month}/${year} | ${hours}:${minutes}:${seconds}`;

    // Cập nhật vào div
    document.getElementById('realtime-clock').textContent = dateTimeString;
}

// Cập nhật mỗi giây
updateClock(); // Chạy ngay lần đầu
setInterval(updateClock, 1000); // Cập nhật mỗi giây
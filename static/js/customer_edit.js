document.addEventListener("DOMContentLoaded", function () {
    const typeField = document.getElementById("id_customer_type");
    if (!typeField) return;

    const cccdInput = document.getElementById("id_cccd");
    const taxInput  = document.getElementById("id_tax_code");

    const cccdGroup = cccdInput ? cccdInput.closest(".form-group-custom") : null;
    const taxGroup  = taxInput  ? taxInput.closest(".form-group-custom")  : null;

    function updateCustomerFields() {
        // 🔒 luôn đảm bảo Loại khách hàng HIỆN
        const typeGroup = typeField.closest(".form-group-custom");
        if (typeGroup) typeGroup.style.display = "flex";

        // reset: hiện hết
        if (cccdGroup) cccdGroup.style.display = "flex";
        if (taxGroup)  taxGroup.style.display  = "flex";

        const value = typeField.value;

        if (value === "personal") {
            // Cá nhân → ẩn MST
            if (taxGroup) taxGroup.style.display = "none";
        }

        if (value === "company") {
            // Doanh nghiệp → ẩn CCCD
            if (cccdGroup) cccdGroup.style.display = "none";
        }
    }

    // chạy lần đầu (load create / edit)
    updateCustomerFields();

    // chạy khi đổi dropdown
    typeField.addEventListener("change", updateCustomerFields);
});
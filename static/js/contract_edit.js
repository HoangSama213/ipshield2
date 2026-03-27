// ===============================
// TAB SWITCHING
// ===============================
document.addEventListener('DOMContentLoaded', function () {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetTab = this.dataset.tab;

            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            this.classList.add('active');
            document
                .querySelector(`[data-content="${targetTab}"]`)
                .classList.add('active');
        });
    });
});

// ===============================
// FORMSET ADD / REMOVE (CHUẨN)
// ===============================
document.addEventListener('click', function (e) {

    // ➕ ADD FORM
    if (e.target.closest('.btn-add')) {
        const btn = e.target.closest('.btn-add');
        const prefix = btn.dataset.prefix;

        const formset = document.getElementById('service-formset');
        const template = document.getElementById('empty-form-template');
        const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);

        if (!formset || !template || !totalForms) return;

        const index = parseInt(totalForms.value);
        let html = template.innerHTML.replace(/__prefix__/g, index);

        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;

        formset.appendChild(wrapper.firstElementChild);
        totalForms.value = index + 1;
    }

    // ❌ REMOVE FORM
    if (e.target.closest('.btn-remove')) {
        const item = e.target.closest('.formset-item');
        if (!item) return;

        const deleteInput = item.querySelector(
            'input[type="checkbox"][name$="-DELETE"]'
        );

        if (deleteInput) {
            deleteInput.checked = true;
            item.style.display = 'none';
        } else {
            item.remove();
        }
    }
});

function toggleEditForm(sessionId) {
    const formDiv = document.getElementById('edit-form-' + sessionId);
    formDiv.classList.toggle('d-none');
}

document.querySelectorAll('.toggle-edit-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
        toggleEditForm(btn.dataset.sessionId);
    });
});
document.addEventListener('DOMContentLoaded', function () {
    var el = document.getElementById('countdown');
    if (!el) return;

    var target = new Date(el.dataset.weddingDate);
    if (isNaN(target.getTime())) return;

    var daysEl = document.getElementById('cd-days');
    var hoursEl = document.getElementById('cd-hours');
    var minutesEl = document.getElementById('cd-minutes');
    var secondsEl = document.getElementById('cd-seconds');

    function update() {
        var diff = Math.max(0, target - new Date());
        daysEl.textContent = Math.floor(diff / 86400000);
        hoursEl.textContent = String(Math.floor(diff / 3600000) % 24).padStart(2, '0');
        minutesEl.textContent = String(Math.floor(diff / 60000) % 60).padStart(2, '0');
        secondsEl.textContent = String(Math.floor(diff / 1000) % 60).padStart(2, '0');
    }

    update();
    setInterval(update, 1000);
});
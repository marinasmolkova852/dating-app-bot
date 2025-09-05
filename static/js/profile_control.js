// const change_form_btn = document.getElementById("change_form");
const about_me_btn = document.getElementById("info");

// Просмотр личной информации
function open_about() {
    let path = '/about_me';
    window.location.href = path;
}

// function change_form() {
//     let path = '/change_form';
//     window.location.href = path;
// }

// change_form_btn.addEventListener('click', change_form);
about_me_btn.addEventListener('click', open_about);


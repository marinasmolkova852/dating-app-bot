
const daysSelect = document.getElementById("day");
for (let i = 1; i <= 31; i++) {
    const option = document.createElement("option");
    if (i < 10){
        day_view = `0${i}`;
    } else{
        day_view = `${i}`;
    }
    option.value = day_view;
    option.textContent = i;
    daysSelect.appendChild(option);
}

// Заполнение списка с месяцами
const monthsSelect = document.getElementById("month");
const months = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
];
months.forEach((month, index) => {
    const option = document.createElement("option");
    if (index < 9){
        month_view = `0${index + 1}`;
    } else {
        month_view = `${index + 1}`;
    }
    option.value = month_view;
    option.textContent = month;
    monthsSelect.appendChild(option);
});

// Заполнение списка с годами (от 2024 до 1924)
const yearsSelect = document.getElementById("year");
for (let year = 2024; year >= 1924; year--) {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    yearsSelect.appendChild(option);
}
// Заполнение списка с разницей в возрасте старше
const gapagesSelect = document.getElementById("gapage");
const gapages = [
    "Категорическое нет", "1-3 года", "4-7 лет", "8-11 лет", "12 и больше", "Не имеет значения"
];
gapages.forEach((gapage) => {
    const option = document.createElement("option");
    option.value = gapage;
    option.textContent = gapage;
    gapagesSelect.appendChild(option);
});

// Заполнение списка с разницей в возрасте младше
const agegapsSelect = document.getElementById("agegap");
const agegaps = [
    "Категорическое нет", "1-3 года", "4-7 лет", "8-11 лет", "12 и больше", "Не имеет значения"
];
agegaps.forEach((agegap) => {
    const option = document.createElement("option");
    option.value = agegap;
    option.textContent = agegap;
    agegapsSelect.appendChild(option);
});
// Заполнение списка со статусом отношений
const statussSelect = document.getElementById("status");
const statuss = [
    "В активном поиске", "Свободна/Свободен", "В отношениях", "Замужем/Женат", "Развод/В разводе"
];
statuss.forEach((status) => {
    const option = document.createElement("option");
    option.value = status;
    option.textContent = status;
    statussSelect.appendChild(option);
});

// Заполнение списка про отношения на расстоянии
const distancesSelect = document.getElementById("distance");
const distances = [
    "Да", "Нет ", "Не уверен(а)"
];
distances.forEach((distance) => {
    const option = document.createElement("option");
    option.value = distance
    option.textContent = distance;
    distancesSelect.appendChild(option);
});

// Заполнение списка про выбор пола
const sexsSelect = document.getElementById("sex");
const sexs = [
    "Мужской", "Женский"
];

sexs.forEach((sex) => {
    const option = document.createElement("option");
    option.value = sex;
    option.textContent = sex;
    sexsSelect.appendChild(option);
});
// Заполнение списка с ориентацией
const orientationsSelect = document.getElementById("orientation");
const orientations = [
    "Гетеросексуал", "Бисексуал", "Гей", "Лесбиянка"
];
orientations.forEach((orientation) => {
    const option = document.createElement("option");
    option.value = orientation;
    option.textContent = orientation;
    orientationsSelect.appendChild(option);
});
// Заполнение списка с целью поисков
const searchingsSelect = document.getElementById("searching");
const searchings = [
    "Найти друга//Найти подругу (дружеские отношения)", "Найти бизнес-партнера//коллегу ", "Найти человека для путешествий", "Построить отношения ", "Найти мужа//Найти жену", "Найти парня//Найти девушку", "Подыскать полового партнера без обязательств (вам должно быть больше 18+)"
];
searchings.forEach((searching) => {
    const option = document.createElement("option");
    option.value = searching;
    option.textContent = searching;
    searchingsSelect.appendChild(option);
});
// Заполнение списка с выбором знака зодиака
const signsSelect = document.getElementById("sign");
const signs = [
    "Овен", "Телец", "Близнецы", "Рак ", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог ", "Водолей", "Рыбы"
];
signs.forEach((sign) => {
    const option = document.createElement("option");
    option.value = sign;
    option.textContent = sign;
    signsSelect.appendChild(option);
});

const give_block = document.querySelector(".give");
function check_give() {
    let checkboxes = give_block.querySelectorAll('input[type="checkbox"]:checked');
    
    if (checkboxes.length >= 5) {
        // Отключаем все неотмеченные чекбоксы
        give_block.querySelectorAll('input[type="checkbox"]:not(:checked)').forEach(function(checkbox) {
            checkbox.disabled = true;
        });
    } else {
        // Включаем все чекбоксы
        give_block.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
            checkbox.disabled = false;
        });
    }
}

const get_block = document.querySelector(".get");
function check_get() {
    let checkboxes = get_block.querySelectorAll('input[type="checkbox"]:checked');
    
    if (checkboxes.length >= 5) {
        // Отключаем все неотмеченные чекбоксы
        get_block.querySelectorAll('input[type="checkbox"]:not(:checked)').forEach(function(checkbox) {
            checkbox.disabled = true;
        });
    } else {
        // Включаем все чекбоксы
        get_block.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
            checkbox.disabled = false;
        });
    }
}

// Добавляем обработчик изменения состояния к каждому чекбоксу
give_block.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
    checkbox.addEventListener('change', check_give);
});

get_block.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
    checkbox.addEventListener('change', check_get);
});
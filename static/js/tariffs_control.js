const initData = window.Telegram.WebApp.initData; // Получаем данные из Telegram Web App
const tariff_start_btn = document.getElementById("pay599");
const tariff_base_btn = document.getElementById("pay999");
const tariff_vip_btn = document.getElementById("pay2999");
const tariff_supervip_btn = document.getElementById("pay9999");
// const profile_btn = document.getElementById('profile');

function tariff_buy(event){
    const button_id = event.target.id;
    let tariff, price, payload;
    
    let promocode = prompt("Есть промокод?\nУкажите его ниже для получения скидки!\n(Если промокода нет, оставьте поле пустым)", '');
    if (promocode === null) return;
    
    if (button_id == 'pay599'){
        tariff = 'СТАРТ';
        price = 599;
        payload = 'tariff_start'
    }
    if (button_id == 'pay999'){
        tariff = 'БАЗОВЫЙ'
        price = 999;
        payload = 'tariff_base'
    }
    if (button_id == 'pay2999'){
        tariff = 'VIP'
        price = 2999;
        payload = 'tariff_vip'
    }
    if (button_id == 'pay9999'){
        tariff = 'SUPER VIP'
        price = 9999;
        payload = 'tariff_supervip'
    }
    
    if (initData) {
        data = {
            'init': String(initData),
            'tariff': tariff,
            'price': price,
            'payload': payload,
            'promocode': promocode
        }
        
        fetch('/buy', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success){
                if (window.Telegram && window.Telegram.WebApp) {
                    window.Telegram.WebApp.close();
                }
            } else {
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}

// function select_profile() {
//     let path = '/profile';
//     window.location.href = path;
// }

// profile_btn.addEventListener('click', select_profile);
tariff_start_btn.addEventListener('click', (event) => tariff_buy(event));
tariff_base_btn.addEventListener('click', (event) => tariff_buy(event));
tariff_vip_btn.addEventListener('click', (event) => tariff_buy(event));
tariff_supervip_btn.addEventListener('click', (event) => tariff_buy(event));
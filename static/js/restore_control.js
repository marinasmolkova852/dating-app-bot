const day_of_birth = document.getElementById('day');
const month_of_birth = document.getElementById('month');
const year_of_birth = document.getElementById('year');
const time_of_birth = document.getElementById('birthtime');
const restore_btn = document.getElementById("restore_btn");
const back_btn = document.getElementById("back_btn");


function filled(){
    for (let i = 1; i <= 31; i++) {
        const option = document.createElement("option");
        if (i < 10){
            day_view = `0${i}`;
        } else{
            day_view = `${i}`;
        }
        option.value = day_view;
        option.textContent = i;
        day_of_birth.appendChild(option);
    }
    
    // Заполнение списка с месяцами
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
        month_of_birth.appendChild(option);
    });
    
    // Заполнение списка с годами (от 2024 до 1924)
    for (let year = 2024; year >= 1924; year--) {
        const option = document.createElement("option");
        option.value = year;
        option.textContent = year;
        year_of_birth.appendChild(option);
    }
}

function restore(){
    const initData = window.Telegram.WebApp.initData; // Получаем данные из Telegram Web App
    let error = false;
    
    if (!initData){
        error = true;
        alert("Ошибка идентификации!");
    }
    
    if (!day_of_birth.value || !month_of_birth.value || !year_of_birth.value || !time_of_birth.value){
        error = true;
        alert("Заполните все поля!");
    }
    
    if (!error){
        
        birth_dt = day_of_birth.value + "." + month_of_birth.value + "." + year_of_birth.value + " " + time_of_birth.value;
        data = {
            'init': String(initData),
            'birth_dt' : birth_dt
        }

        fetch('/try_restore', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success){
                alert(data.message);
                let path = "/form";
                window.location.href = path;
            } 
            else{
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
        
    }
}

function back(){
    window.location.href = '/form';
}

document.addEventListener("DOMContentLoaded", filled);
restore_btn.addEventListener("click", restore);
back_btn.addEventListener("click", back);
const initData = window.Telegram.WebApp.initData; // Получаем данные из Telegram Web App

// function send_user_data(){
//     const str_init = String(initData);
//     let data = {
//         'init': str_init
//     };
    
//     fetch('/check', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(data),
//     })
//     .then((response) => response.json())
//     .then((data) => {
//         if (data.status){
//             let path = '/profile';
//             window.location.href = path;
//         }
//     })
//     .catch((error) => {
//         console.error('Error:', error);
//     });
// }

function send_user_data(){
    fetch(`/form?auth=${encodeURIComponent(initData)}`)
    .then((response) => {
        if (response.redirected){
            window.location.href = response.url;
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


if (initData) send_user_data();
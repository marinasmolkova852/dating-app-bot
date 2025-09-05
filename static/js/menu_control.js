const profile_btn = document.getElementById("profile");
const payment_btn = document.getElementById("payment");
const match_btn = document.getElementById("match");
const speed_btn = document.getElementById("speedometr");
const love_btn = document.getElementById("love_in_me");


function go_to_profile() {
    if (window.location.pathname != '/profile'){
        let path = '/profile';
        window.location.href = path;
    }
}

function go_to_tariffs() {
    if (window.location.pathname != '/tariffs'){
        let path = '/tariffs';
        window.location.href = path;
    }
}

function go_to_match() {
    if (window.location.pathname != '/match'){
        let path = '/match';
        window.location.href = path;
    }
}

function go_to_speedometr() {
    if (window.location.pathname != '/speed'){
        let path = '/speed';
        window.location.href = path;
    }
}


function go_to_love_in() {
    if (window.location.pathname != '/love'){
        let path = '/love';
        window.location.href = path;
    }
}


profile_btn.addEventListener('click', go_to_profile);
payment_btn.addEventListener("click", go_to_tariffs);
match_btn.addEventListener("click", go_to_match);
speed_btn.addEventListener("click", go_to_speedometr);
love_btn.addEventListener("click", go_to_love_in);

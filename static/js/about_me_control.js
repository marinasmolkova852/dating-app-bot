const delete_form_btn = document.getElementById("delete_form");

function delete_form(){
    const answer = confirm("Вы действительно хотите удалить анкету?"); // Отображает окно с сообщением "Вы уверены?"
    
    if (answer) {
        fetch('/delete_form')
        .then((response) => response.json())
        .then((data) => {
            if (data.success){
                alert(data.message);
                let path = "/form";
                window.location.href = path;
            } 
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}

delete_form_btn.addEventListener("click", delete_form);
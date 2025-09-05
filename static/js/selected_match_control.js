document.querySelector('.agree').addEventListener('click', function() {
    const agree_addr = `/agree/${match_id}`;
    
    fetch(agree_addr, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'match_id': match_id}),
    })
    .then((response) => response.json())
    .then((data) => {
        alert(data.message);
        if (data.status){

            let path = "/match";
            window.location.href = path;
        } 
    })
    .catch((error) => {
        console.error('Error:', error);
    });
    
});

document.querySelector('.deny').addEventListener('click', function() {
    const deny_addr = `/deny/${match_id}`;
    
    fetch(deny_addr, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'match_id': match_id}),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.status){
            let path = "/match";
            window.location.href = path;
        } else {
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
    
});
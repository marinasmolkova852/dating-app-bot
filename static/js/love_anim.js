document.getElementById("much").addEventListener("click",
    function know() {
    document.querySelector(".heart-clip").checked = true;
	setTimeout(function(){
    document.getElementById("know_love").style.display = "block";
	document.getElementById("datelove").style.display = "none";
	document.getElementById("number").style.display = "block";
	document.getElementById("howlove").style.display = "none";
	document.querySelector(".heart-container").style.display = "none";
    },3000)
    });
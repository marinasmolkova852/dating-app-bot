document.getElementById("count").addEventListener("click",
    function sovmest() {
	document.querySelector(".arrow").classList.toggle("arrow-rotate"); 
	setTimeout(function(){
    document.getElementById("sovmest_info").style.display = "block";
	document.getElementById("headline").style.display = "none";
	document.getElementById("speedomter" ).style.display = "none";
  },3000)
    });
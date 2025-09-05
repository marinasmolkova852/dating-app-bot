// Кнопка стартовой страницы
document.getElementById("nextto").addEventListener("click",
    function start() {
        document.getElementById("regist").style.display = "block";
        document.getElementById("hello").style.display = "none";
        document.getElementById("next").style.display = "block";
        document.getElementById("rectangle1").style.display = "block";
        document.getElementById("return").style.display = "block";
    });
    // Первая кнопка далее с открыванием анкеты
document.getElementById("next").addEventListener("click",
    function regist() {
        document.getElementById("regist1").style.display = "none";
        document.getElementById("regist2").style.display = "block";
        document.getElementById("next").style.display = "none";
        document.getElementById("next1").style.display = "block";
        document.getElementById("rectangle2").style.display = "block";
        document.getElementById("return").style.display = "block";
    });

// Первая кнопка назад к вводу имени со страницы анкеты
document.getElementById("return").addEventListener("click",
    function back1() {
        document.getElementById("regist1").style.display = "block";
        document.getElementById("regist2").style.display = "none";
        document.getElementById("next").style.display = "block";
        document.getElementById("next1").style.display = "none";
        document.getElementById("rectangle2").style.display = "none";
        document.getElementById("return").style.display = "none";
      
   });
   // Кнопка на тарифы
  //document.getElementById("tarifs").addEventListener("click",
   //   function tar() {
    //      document.getElementById("tarifs").style.display = "block";
   //       document.getElementById("regist3").style.display = "none";
   //       document.getElementById("rectangle1").style.display = "none";   
   //       document.getElementById("rectangle2").style.display = "none";  
   //       document.getElementById("rectangle3").style.display = "none";
   //      document.getElementById("return1").style.display = "none";
  //  });
// Кнопка назад из тарифов
 // document.getElementById("cl").addEventListener("click",
  //    function ank() {
  //        document.getElementById("tarifs").style.display = "none";
  //        document.getElementById("regist3").style.display = "block";
   //       document.getElementById("rectangle1").style.display = "block";  
   //       document.getElementById("rectangle2").style.display = "block";  
   //       document.getElementById("rectangle3").style.display = "block";
     //   document.getElementById("return1").style.display = "block";
  //  });
    // Кнопка на пользовательское соглашение
document.getElementById("sog").addEventListener("click",
    function sogl() {
        document.getElementById("soglash").style.display = "block";
        document.getElementById("regist2").style.display = "none";
	document.getElementById("regist3").style.display = "none";
	document.getElementById("rectangle1").style.display = "none";   
	document.getElementById("rectangle2").style.display = "none";   
	document.getElementById("rectangle3").style.display = "none"; 
    //   document.getElementById("return1").style.display = "none";
   });
   // Кнопка закрыть пользовательское соглашение
   document.getElementById("clos").addEventListener("click",
    function checkread() {
        document.getElementById("soglash").style.display = "none";
       document.getElementById("regist3").style.display = "none";
	document.getElementById("rectangle3").style.display = "none"; 
    document.getElementById("regist2").style.display = "block";
	document.getElementById("rectangle1").style.display = "block";  
	document.getElementById("rectangle2").style.display = "block";
    //   document.getElementById("return1").style.display = "block";
   });
   
   // Кнопка на политику
document.getElementById("pol").addEventListener("click",
    function polit() {
    document.getElementById("politika").style.display = "block";
    document.getElementById("regist2").style.display = "none";
	document.getElementById("regist3").style.display = "none";
	document.getElementById("rectangle1").style.display = "none";   
	document.getElementById("rectangle2").style.display = "none";   
	document.getElementById("rectangle3").style.display = "none"; 
      //   document.getElementById("return1").style.display = "none";
   });
// Кнопка закрыть политику
document.getElementById("cl").addEventListener("click",
    function closed() {
    document.getElementById("politika").style.display = "none";
	document.getElementById("regist3").style.display = "none";
	document.getElementById("rectangle3").style.display = "none"; 
    document.getElementById("regist2").style.display = "block";
	document.getElementById("rectangle1").style.display = "block";  
	document.getElementById("rectangle2").style.display = "block";   
       //  document.getElementById("return1").style.display = "block";
   });
   
 // let tg = window.Telegram.WebApp;
  //let btn = document.getElementById("pay");

 // btn.addEventListener("click", () => {
  //  if (tg.isExpanded) {
   //   tg.close();
   // } else {
   //   tg.expand();
   //   setTimeout(() => tg.close(), 50);
  //  }
  //});
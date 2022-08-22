

function show_checkbox(){
event.preventDefault()
items = document.getElementsByClassName("list-checkbox")
for (let i=0; i<items.length; i++){
    items[i].classList.remove("hide");
}
btns= document.getElementsByClassName("delete-list-btn")
for (let i=0; i < btns.length; i++){
    btns[i].classList.remove("hide");
}
}

function hide_checkbox(){
event.preventDefault()
items = document.getElementsByClassName("list-checkbox")
for (let i=0; i<items.length; i++){
    items[i].classList.add("hide");
}
btns=document.getElementsByClassName("delete-list-btn")
for (let i=0; i<btns.length; i++){
    btns[i].classList.add("hide");
}
}




$(document).ready(function(){
  $("#myInput").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#myTable tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});
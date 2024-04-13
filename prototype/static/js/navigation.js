// Get all the buttons that open the modals
var btns = document.querySelectorAll(".myBtn");

// Get all the modals
var modals = document.querySelectorAll(".myModal");

// Get all the <span> elements that close the modals
var spans = document.querySelectorAll(".close");

// When the user clicks a button, open the corresponding modal 
btns.forEach((btn, index) => {
  btn.onclick = function() {
    modals[index].style.display = "block";
  }
});

// When the user clicks on <span> (x), close the corresponding modal
spans.forEach((span, index) => {
  span.onclick = function() {
    modals[index].style.display = "none";
  }
});

// When the user clicks anywhere outside of a modal, close it
window.onclick = function(event) {
  modals.forEach((modal, index) => {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  });
}

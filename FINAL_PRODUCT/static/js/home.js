// Get all the images that open the modals
var imgs = document.querySelectorAll(".myImg");

// Get all the modals
var modals = document.querySelectorAll(".myModal");

// Get all the <span> elements that close the modals
var spans = document.querySelectorAll(".close");

// Get all the modal images
var modalImgs = document.querySelectorAll(".imgModal");

// When the user clicks an image, open the corresponding modal 
imgs.forEach((img, index) => {
  img.addEventListener('click', function() {
    modals[index].style.display = "block";
    modalImgs[index].src = this.src;
  });
});

// When the user clicks on <span> (x), close the corresponding modal
spans.forEach((span, index) => {
  span.addEventListener('click', function() {
    modals[index].style.display = "none";
  });
});

// When the user clicks anywhere outside of a modal, close it
window.addEventListener('click', function(event) {
  modals.forEach((modal, index) => {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  });
});

// OPEN FORM CLOSE FORM FOR UPDATE
// Open modal function
function openModal(modalId) {
  var modal = document.getElementById(modalId);
  modal.style.display = "block";
}

// Close modal function
function closeModal(modalId) {
  var modal = document.getElementById(modalId);
  modal.style.display = "none";
}


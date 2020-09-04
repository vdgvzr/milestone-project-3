/* This .js file contains functions that displays
a quote at random in index.html. The quotes are pulled
from the for loop and stored in an array which is then
randomised and changed with a fade after 15 seconds */

// Define the variable to be used here
let count = 0, quotes = [];

/* Pull the quotes from the index.html for loop
and push them all to the quotes array above */
$(".quote-content").each(function() {
    quotes[count++]=$(this).text();
});

/* Function that randomises the quotes in the array
to be called within the main change() function */
function randomQuote() {
    let randomNumber = Math.floor(Math.random() * (quotes.length));
    document.getElementById('quote-box').innerHTML = quotes[randomNumber];
}

/* Iterates through the randomised array and changes
each quote with a fade in after 15 seconds */
function change() {
    if (count >= quotes.length) count = 0;
    $("#quote-box").html(quotes[count++]);
    $("#quote-box").fadeIn("slow").animate({opacity: 0.8}, 15000).fadeOut("slow",
        function() {
            return change()
        }
    );
    randomQuote();
}

change();
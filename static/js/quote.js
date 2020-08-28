let count = 0, quotes = [];

$(".quote-content").each(function() {
    quotes[count++]=$(this).text();
});

function randomQuote() {
    let randomNumber = Math.floor(Math.random() * (quotes.length));
    document.getElementById('quote-box').innerHTML = quotes[randomNumber];
}

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
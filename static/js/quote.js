let count = 0, quotes = [];

$(".quote-content").each(function() {
    quotes[count++]=$(this).text();
});

function randomQuote() {
    let randomNumber = Math.floor(Math.random() * (quotes.length));
    document.getElementById('quote-box').innerHTML = quotes[randomNumber];
}

randomQuote();

function change() {
    if (count >= quotes.length) count = randomQuote();
    $("#quote-box").html(quotes[count++]);
    $("#quote-box").fadeIn("slow").animate({opacity: 0.8}, 10000).fadeOut("slow",
        function() {
            return change()
        });
}

change();
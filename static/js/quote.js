let count = 0, quotes = [];

$(".quote-content").each(function() {
    quotes[count++]=$(this).text();
});

function change() {
    if (count >= quotes.length) count = 0;
    $("#quote-box").html(quotes[count++]);
    $("#quote-box")
        .fadeIn("slow").animate({opacity: 0.9}, 10000).fadeOut("slow",
        function() {
            return change()
        });
}

change();
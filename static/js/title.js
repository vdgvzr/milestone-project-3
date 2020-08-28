$(document).ready(function() {
    $('#book_title').keyup(function(event) {
        $('#book_title').css('textTransform', 'capitalize')
    });
    $('#book_author').keyup(function(event) {
        $('#book_author').css('textTransform', 'capitalize')
    });
    $('#genre').keyup(function(event) {
        $('#genre').css('textTransform', 'capitalize')
    });
});
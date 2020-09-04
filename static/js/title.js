/* To generate consistency with titles, when adding a book,
the title, author and genre input fields are all capitalised
as it is being typed. (Note that this is purely visual and the
value that is being input will be sent to the database regardless.
In order to display capitalised values, this will be done within the
appropriate display fields across the templates) */
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
/* Function to toggle the password input
type between password and text whenever
the function is called by the checkbox in
register.html and login.html */
function passwordShow() {
    /* Define the variable x as any element within
    the document with the id of 'password' */
    let x = document.getElementById('password');
    // If the clicked element type is password, toggle text
    if (x.type === 'password') {
        x.type = 'text';
    // Else revert back to password
    } else {
        x.type = 'password';
    }
}
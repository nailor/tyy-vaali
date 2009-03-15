$(document).ready(
    function() {
        $('#submitnagger').hide();
        $('input').removeAttr('disabled');
        $('#opnrofield').keypress(
            function(e) {
                if (e.which == 13) {
                    // Line feed hit, nag nagity nag nag
                    $('#submitnagger').show();
                    $('#submits').addClass('error');
                }
            });
        $('#submits button').click(
            function() {
                var button = $(this);
                $('input').removeClass('error');
                $('#submits').removeClass('error');
                $('#submitnagger').hide();
                if (confirm("Turun yliopisto: Jyrki Pulliainen, 65534. Onko oikein?")) {
                    console.log('blip');
                }
            }
        );
    });
function o2str(org) {
    if (org == 'utu.fi') {
        return 'Turun yliopisto';
    } else {
        return 'Turun kauppakorkeakoulu';
    }
}

function disable() {
    $('button').attr('disabled', true);
    $('#opnrofield').attr('disabled', true);
}

function enable() {
    $('button').removeAttr('disabled');
    $('#opnrofield').removeAttr('disabled');
    $('#opnrofield').focus();
}
function ajax_error(data, status) {
    $('#ajaxerror').show();
    enable();
    $('#statusdata').text('Syötä opiskelijanumero');
}
function display_errors(errors) {
    for (var i in errors) {
        if (i != '__all__') {
            $('[name=' + i +']').addClass('error');
        } else {
            alert(errors[i]);
        }
    }
}

function handle_vote(data, status) {
    if (data.errors) {
        display_errors(data.errors);
    } else {
        alert(data['ok']);
    }
}

function handle_check(data, status) {
    if (data.errors) {
        display_errors(data.errors);
    } else {
        data = data[0];
        var cmsg = o2str(data.fields.organization) + '\n'
            + data.fields.lastname + ", " + data.fields.firstname + " ("
            + data.fields.personnumber + ")\n\n"
            + "Onko oikein?";
        if (confirm(cmsg)) {
            var voter_data = {
                'number': data.fields.personnumber,
                'organization': data.fields.organization,
                'place': $('#location').data('loc')
            };
            $.ajax(
                {
                    beforeSend: start_send,
                    complete: send_done,
                    data: voter_data,
                    dataType: 'json',
                    error: ajax_error,
                    success: handle_vote,
                    type: 'POST',
                    url: '/tarkistus/commit/'
                });

        }
    }
}
function start_send() {
    disable();
    $('#statusdata').text('Käsitellään...');
    $('#ajax-loader').clone().show().prependTo('#statusdata');
}
function send_done() {
    enable();
    $('#statusdata').text('Syötä opiskelijanumero');
}
function do_check() {
    var button = $(this);
    $('#statusdata').show();
    $('.error').removeClass('error');
    $('#submitnagger').hide();
    var data = {
        'number': $('#opnrofield').val(),
        'place': $('#location select').val(),
        'organization': button.attr('id')
    };
    $.ajax(
        {
            beforeSend: start_send,
            complete: send_done,
            data: data,
            dataType: 'json',
            error: ajax_error,
            success: handle_check,
            type: 'POST',
            url: '/tarkistus/whois/'
        });
}

$(document).ready(
    function() {
        $('#submitnagger').hide();
        $('#location-change').hide();
        $('#ajaxerror').hide();
        $('#ajax-loader').hide();
        disable();
        $('#opnrofield').keypress(
            function(e) {
                if (e.which == 13) {
                    // Line feed hit, nag nagity nag nag
                    $('#submitnagger').show();
                    $('#submits').addClass('error');
                }
            });
        $('#submits button').click(do_check);
        $('#location-change').click(
            function() {
                $('#location').removeData('loc');
                $('#location select option:first').attr('selected', true);
                disable();
                $('#location-change').hide();
                $('#location span.loc').text('');
                $('#location select').show();
            });
        $('#location select').change(
            function() {
                var select = $(this);
                if (select.val()) {
                    $('#location').data('loc', select.val());
                    $('#location span.loc').text(
                        select.find(':selected').text()
                    );
                    select.hide();
                    $('#location-change').show();
                    enable();
                }
            });
        $('#ajaxerror a').click(
            function() {
                $(this).parent().hide();
            });
        $('#opnrofield').focus(function() { $(this).select(); });
    });
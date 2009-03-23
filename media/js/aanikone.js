function o2token(org) {
    if (org == 'utu.fi')
        return 'TYY';
    return "TuKY";
}

function select_ticket() {
    var a = $(this);
    $('#opnrofield').val(a.data('number'));
    // Can't use #utu.fi here, it causes jqeury to look out for
    // id utu with class fi.
    // This here is a somewhat performance loss, but...
    $('[id=' + a.data('org') + ']').click();
}

function update_ticket_list() {
    function _got(data, status) {
        var ul = $('<ul></ul>');
        for (var i=0; i<data.length; i++) {
            var li = $('<li></li>');
            var a = $('<a href="javascript:;"></a>');
            var text = o2token(data[i].organization);
            text += ' / ' + data[i].number;
            a.text(text);
            a.click(select_ticket);
            a.data('number', data[i].number);
            a.data('org', data[i].organization);
            a.appendTo(li);
            li.appendTo(ul);
        }
        $('#voterspanel ul').replaceWith(ul);
    }
    $.ajax(
        {
            dataType: 'json',
            error: ajax_error,
            success: _got,
            type: 'GET',
            url: '/tarkistus/list/' + $('#location').data('loc') + '/'
        });
}

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
    /* Done here, the list keeps up to date unless there's
     * simultaneous vote checkers in the same location. */
     update_ticket_list();
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
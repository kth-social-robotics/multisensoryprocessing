$(document).ready(function() {
    var current_page = "dialog"

    var socket = io.connect('http://' + document.domain + ':' + location.port);

    var beliefs = {
        'white': 0.0,
        'blue': 0.0,
        'black': 0.0,
        'brown': 0.0,
        'pink': 0.0,
        'orange': 0.0,
    }

    function updateVoteHtml(name) {
      var template = $('#template-vote').html();
      Mustache.parse(template);   // optional, speeds up future uses
      var rendered = Mustache.render(template, {name: name});
      $('#voting').html(rendered);
    }

    function updateBeliefHtml() {
      var template = $('#template').html();
      Mustache.parse(template);   // optional, speeds up future uses
      var rendered = Mustache.render(template, {beliefs: beliefs});
      $('#beliefs').html(rendered);
    }
    updateBeliefHtml();
    updateVoteHtml('N/A')


    socket.on('update_belief_interface', function(data) {
      beliefs[data['participant']] = data['belief'].toFixed(2);
      updateBeliefHtml();
    });

    socket.on('display_suggested_vote', function(data) {
      $('#argument-vote li').css('background-color', 'white')
      $('#argument-vote li[data-participant=' + data['participant'] + ']').css('background-color', '#FFEDCC')

    });


    function reset() {
        $('.list-group').removeClass('dim');
    }

    var state = 0;
    var combo = [];
    var stop = false;
    $('html').on('keydown', function(event) {
        if (stop) return;
        if ($(event.target).attr('id') === 'name') return true;
        var keyPressed = event.key.toLowerCase();
        combo.push(keyPressed);
        console.log(combo.sort().join('-'))

        if (combo.length == 2) {
            var modifier = null;
            if (combo.indexOf('alt') !== -1){
                modifier = 'support';
            } else if (combo.indexOf('control') !== -1){
                modifier = 'defend';
            } else if (combo.indexOf('shift') !== -1){
                //console.log(current_page.indexOf('small-talk'))
                if(current_page.indexOf('small-talk') !== -1){
                    modifier = 'small_talk'
                }else if(current_page.indexOf('dialog') !== -1){
                    modifier = 'accuse';
                }
            }

            if (modifier) {
                var participant = combo.filter(item => ['alt', 'control', 'shift','meta'].indexOf(item) === -1)[0]
                switch(participant) {
                    case '§':
                    case '±':
                      $.get(`/dialog_act?action=${modifier}&participant=general`)
                      break;
                    case '0':
                    case 'º':
                    case ')':
                    case '=':
                    case '≠':
                      $.get(`/dialog_act?action=${modifier}&participant=self`)
                      break;
                    case '1':
                    case '¡':
                    case '!':
                    case '':
                      $.get(`/dialog_act?action=${modifier}&participant=black`)
                      break;
                    case '2':
                    case '™':
                    case '@':
                    case '"':
                      $.get(`/dialog_act?action=${modifier}&participant=brown`)
                      break;
                    case '3':
                    case '£':
                    case '#':
                    case '€':
                      $.get(`/dialog_act?action=${modifier}&participant=orange`)
                      break;
                    case '4':
                    case '¢':
                    case '$':
                    case '£':
                      $.get(`/dialog_act?action=${modifier}&participant=blue`)
                      break;
                    case '5':
                    //case '§':
                    case '^':
                    case '%':
                    case '‰':
                      $.get(`/dialog_act?action=${modifier}&participant=pink`)
                      break;
                    case '6':
                    case '¶':
                    case '&':
                    case '¶':
                      $.get(`/dialog_act?action=${modifier}&participant=white`)
                      break;
                }

            }

        }

        if (current_page.indexOf('argue-vote') !== -1){
            $.get('/vote');
            switch(keyPressed){
                case '§':
                    $.get(`/dialog_act?action=summary`)
                    break;
                case '1':
                    $.get(`/dialog_act?action=vote&participant=black`)
                    break;
                case '2':
                    $.get(`/dialog_act?action=vote&participant=brown`)
                    break;
                case '3':
                    $.get(`/dialog_act?action=vote&participant=orange`)
                    break;
                case '4':
                    $.get(`/dialog_act?action=vote&participant=blue`)
                    break;
                case '5':
                    $.get(`/dialog_act?action=vote&participant=pink`)
                    break;
                case '6':
                    $.get(`/dialog_act?action=vote&participant=white`)
                    break;
            }
        }


        switch(combo.sort().join('-')) {
            case 'q':
              socket.emit("say", {"text": "yes"})
              //$.get('/say?text=yes');
              break;
            case 'w':
              $.get('/say?text=no')
              break;
            case 'e':
              $.get('/say?text=maybe')
              break;
            case 'r':
              $.get('/gesture?gesture_name=sleep')
              break;
            case 't':
              $.get(`/dialog_act?action=backchannel`)
              break;
            case 'shift':
              $('.list-group:not(#accuse)').addClass('dim');
              break;
            case 'control':
              $('.list-group:not(#defend)').addClass('dim');
              break;
            case 'alt':
              $('.list-group:not(#support)').addClass('dim');
              break;

        }
    });
    $('html').on('keyup', function(event) {
        combo = [];
        stop = false;
        reset();
    });

    $(".change-pane").on("click", function() {
        $(".tab-content .tab-pane").removeClass("active")
        $("#" + $(this).data("page")).addClass("active")
        current_page = $(this).data("page")
    })
});

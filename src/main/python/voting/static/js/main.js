$(function() {
    participants = {
        'red': ['orange', 'blue', 'brown', 'pink', 'black', 'white', 'red'],
        'black': ['blue', 'pink', 'orange', 'white', 'brown', 'red', 'black'],
        'brown': ['pink', 'white', 'blue', 'red', 'orange', 'black', 'brown'],
        'orange': ['white', 'red', 'pink', 'black', 'blue', 'brown', 'orange'],
        'blue': ['red', 'black', 'white', 'brown', 'pink', 'orange', 'blue'],
        'pink': ['black', 'brown', 'red', 'orange', 'white', 'blue', 'pink'],
        'white': ['brown', 'orange', 'black', 'blue', 'red', 'pink', 'white']
    };

    function getParameterByName(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    var participant = getParameterByName('participant') || 'red';

    $('.btn').on('click', function () {
        console.log(participant)
        if(confirm('are you sure you want to vote for participant ' + $(this).html() + '?')) {
            $.get('/vote?participant=' + participant + '&vote_for=' + $(this).html().toLowerCase())
        }
    })

    function changeColors(participant) {
      for (var i =0; i < 7; i++) {
          color = participants[participant][i];
          var fontColor = 'white';
          if (color == 'white') {
              fontColor = 'black';
          }
          $('#col' + (i + 1)).css('background-color', color).css('color', fontColor).html(color);
      }
    }

    $('#select_participant').on('change', function() {
        participant = $(this).val();
        changeColors($(this).val())
    })




    $('#select_participant').val(participant)
    changeColors(participant)


});

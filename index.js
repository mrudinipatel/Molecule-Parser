$(document).ready(function () {
  //show table when page is loaded
  $.ajax({
    url: '/showTable',
    type: 'GET',
    success: function (response) {
      const table = $('#element_table');

      for (let i = 0; i < response.length; i++) {
        const element = response[i];
        const newRow = $('<tr>');

        newRow.append($('<td>').text(element[0]));
        newRow.append($('<td>').text(element[1]));
        newRow.append($('<td>').text(element[2]));
        newRow.append($('<td>').text(element[3]));
        newRow.append($('<td>').text(element[4]));
        newRow.append($('<td>').text(element[5]));
        newRow.append($('<td>').text(element[6]));
        newRow.append(
          $('<td>').html('<button class="del-btn">Delete</button>')
        );
        table.append(newRow);
      }
    },
  });

  //file upload section
  $('#form_id').submit(function (e) {
    e.preventDefault();
    const file = $('#form_id')[0];
    const fdata = new FormData(file);

    $.ajax({
      data: fdata,
      url: '/molecule',
      type: 'POST',
      processData: false,
      contentType: false,
      cache: false,
      success: function (response) {
        alert('File successfully uploaded!');
        $('#all_mols').append(new Option(response, response));
      },
      error: function () {
        alert('Please enter a valid .sdf file with unique molecule name.');
      },
    });
  });

  //display section
  $('#all_mols').change(function (e) {
    e.preventDefault();
    const selectedOption = $(this).val();

    $.ajax({
      data: selectedOption,
      url: '/selected',
      type: 'POST',
      processData: false,
      contentType: false,
      cache: false,
      success: function (response) {
        var svgDom = $(response).find('svg')[0];

        $('#svg_img').children().replaceWith('');
        $('#svg_img').append(svgDom);
      },
    });

    //rotate section
    $('#rotate_form').submit(function (e) {
      e.preventDefault();
      const file = $('#rotate_form')[0];
      const mol = selectedOption;

      const fdata = new FormData(file);
      fdata.append("molVal", mol);

      $.ajax({
        data: fdata,
        url: '/rotate',
        type: 'POST',
        processData: false,
        contentType: false,
        cache: false,
        success: function (response) {
          var svgDom = $(response).find('svg')[0];

          $('#svg_img').children().replaceWith('');
          $('#svg_img').append(svgDom);
        },
      });
    });
  });

  //add elements section
  $('#addEls').submit(function (e) {
    e.preventDefault();
    const file = $('#addEls')[0];
    const fdata = new FormData(file);

    $.ajax({
      data: fdata,
      url: '/addElements',
      type: 'POST',
      processData: false,
      contentType: false,
      cache: false,
      success: function (response) {
        alert('Element successfully added!');

        const table = $('#element_table');
        const newRow = $('<tr>');

        newRow.append($('<td>').text(response.num));
        newRow.append($('<td>').text(response.code));
        newRow.append($('<td>').text(response.el_name));
        newRow.append($('<td>').text(response.c1));
        newRow.append($('<td>').text(response.c2));
        newRow.append($('<td>').text(response.c3));
        newRow.append($('<td>').text(response.rad));
        newRow.append(
          $('<td>').html('<button class="del-btn">Delete</button>')
        );
        table.append(newRow);
      },
      error: function () {
        alert("Please ensure 'Element Code' is a unique value.");
      },
    });
  });

  //delete element button section
  $('#element_table').on('click', 'button', function (e) {
    e.preventDefault();
    const row = $(this).closest('tr');
    const el_code = row.find('td:eq(1)').text();
    row.remove();

    const rowData = { element_code: el_code };

    $.ajax({
      data: JSON.stringify(rowData),
      url: '/removeRow',
      type: 'POST',
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      success: function (response) {
        row.remove();
      },
    });
  });

});



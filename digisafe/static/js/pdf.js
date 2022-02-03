// import { jsPDF } from "./jsPDF-1.3.2/jspdf.js";

// Default export is a4 paper, portrait, using millimeters for units
const pdfDoc = new jsPDF();

var filename = document.getElementById('filepdf').textContent;
var url = "/document/"+filename;
console.log(url);
loadPdf();

function loadPdf() {
    // pdfDoc .loadFile(url, false, responsePDF());
    pdfDoc.text("Hello world!", 10, 10);
    var string = pdfDoc.output('datauristring');
    var embed = "<embed width='100%' height='100%' src='" + string + "'/>";
    var node = document.createElement("embed");
    node.setAttribute('width', '100%');
    node.setAttribute('height', '100%');
    node.setAttribute('src', string);
    var el = document.getElementById('the-canvas');
    el.appendChild(node);
    // var x = window.open();
    // x.document.open();
    // x.document.write(embed);
    // x.document.close();
}

function responsePDF() {
    console.log("in callback")
    doc.save("pdfjs.pdf");
}

/*Salva file sul server
var doc = new jsPDF();
$('#generatereport').click(function()
{
    doc.fromHTML(
        $('#lppresults'), 15, 15,
        {width: 170},
        function()
        {
            var blob = doc.output('blob');

            var formData = new FormData();
            formData.append('pdf', blob);

            $.ajax('/upload.php',
            {
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(data){console.log(data)},
                error: function(data){console.log(data)}
            });
        }
    );
});

in php ...
<?php
move_uploaded_file(
    $_FILES['pdf']['tmp_name'], 
    $_SERVER['DOCUMENT_ROOT'] . "/uploads/test.pdf"
);
?>
*/
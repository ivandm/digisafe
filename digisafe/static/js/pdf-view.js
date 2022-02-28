// If absolute URL from the remote server is provided, configure the CORS
// header on that server.


// Loaded via <script> tag, create shortcut to access PDF.js exports.
var pdfjsLib = window["pdfjs-dist/build/pdf"];

// The workerSrc property shall be specified.
pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/js/pdfjs-2.12.313-dist/build/pdf.worker.js';

// Asynchronous download of PDF
var loadingTask = null;

// script variable declaretion
var pdfDoc = null;
var pageNum = null;
var scale = null;
var canvas = null;
var context = null;
var shadow  = null;
var pageRendering = false,
    pageNumPending = null,
    pdfX = null,
    pdfY = null,
    mouseX = null,
    mouseY = null;

var signsDict = {};
/**
* Get page info from document, resize canvas accordingly, and render page.
* @param num Page number.
*/
function renderPage(pageNum){
    pageRendering = true;
    pageNum = pageNum;
    pdfDoc.getPage(pageNum).then(function(page) {
        // console.log('Page loaded');
        
        var viewport = page.getViewport({scale: scale});
        // Prepare canvas using PDF page dimensions
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        canvas.parentElement.style.width = viewport.height+"px";

        // Render PDF page into canvas context
        var renderContext = {
          canvasContext: context,
          viewport: viewport
        };
        var renderTask = page.render(renderContext);
        renderTask.promise.then(function () {
          // console.log('Page rendered');
          pageRendering = false;
          if (pageNumPending !== null) {
            // New page rendering is pending
            renderPage(pageNumPending);
            pageNumPending = null;
          }
          //oggetto asincrono. Deve stare qui altrimenti disegna prima del pdf
          drawSign(); 
        });
        
  });
  // Update page counters
  document.getElementById('page_num').textContent = pageNum;
  
}


function drawPdf(loadingTask){
    loadingTask.promise.then(function(pdf_) {
      // console.log('PDF loaded');
      pdfDoc = pdf_;
      
      // Fetch the first page
      pageNum = 1;
      
      document.getElementById('page_count').textContent = pdfDoc.numPages;
      
      // Initial/first page rendering
      renderPage(pageNum);
      
    }, function (reason) {
      // PDF loading error
      console.error(reason);
      
    });
}

/**
 * If another page rendering in progress, waits until the rendering is
 * finised. Otherwise, executes rendering immediately.
 */
function queueRenderPage(num) {
  if (pageRendering) {
    pageNumPending = num;
  } else {
    renderPage(num);
  }
}


/**
 * Displays previous page.
 */
function onPrevPage() {
  // console.log("onPrevPage");
  if (pageNum <= 1) {
    return;
  }
  pageNum--;
  queueRenderPage(pageNum);
}


/**
 * Displays next page.
 */
function onNextPage() {
  console.log("onNextPage");
  if (pageNum >= pdfDoc.numPages) {
    return;
  }
  pageNum++;
  queueRenderPage(pageNum);
}


// Position mouse client
function dragMoveListener(event) {
    // console.log(canvas);
    mouseX = event.offsetX;
    mouseY = event.offsetY;
    
    pdfX = event.offsetX;
    pdfY = canvas.height-event.offsetY;
    // document.getElementById('pdf-posX').textContent = pdfX;
    // document.getElementById('pdf-posY').textContent = pdfY;
    // console.log("offset", mouseX, mouseY);
    // console.log("pdf", pdfX, pdfY);
  }


// inserisce le nuove firme per ogni pagina al dopio click
function newSign() {
        x = mouseX;
        y = mouseY;

        var draws = {};
        draws.pdfcoord  = [pdfX, pdfY, 100, 50];
        draws.file_page = pageNum;
        draws.coord     = [x, y, 100, 50];
        draws.img       = source_img;
        draws.txt       = txt_sign;
        appendPageSign(pageNum, draws)
        
        drawSign();
        removeLastSign.disabled = false;
        saveFile.disabled = false;
    }


function appendPageSign(page, signDict){
    var l = signsDict[page] || [];
    l.push(signDict);
    signsDict[page] = l;
    // console.log("newSign added to page: ",page ,signsDict[page] );
}


// ridisegna i rettangoli memorizzati ad ogni cambio pagina
function drawSign() {
        context.strokeStyle = "black";
        context.font = '14px serif';
        context.textBaseline = "middle";
        var boxs = signsDict[pageNum];
        for(var k in boxs){
            // console.log(k);
            draws = boxs[k];
            context.strokeRect(scale*draws.coord[0]-scale*draws.coord[2]/2, scale*draws.coord[1]-scale*draws.coord[3]/2, draws.coord[2], draws.coord[3]);
            context.drawImage(draws.img, scale*draws.coord[0]-scale*draws.coord[2]/2, scale*draws.coord[1]-scale*draws.coord[3]/2, draws.coord[2], draws.coord[3]);
            var lentext = context.measureText(draws.txt)
            context.fillText(draws.txt, scale*draws.coord[0]-lentext.width/2, scale*draws.coord[1]);
        }
    }


function refreshPdfPage(){
    queueRenderPage(pageNum);    
}


function delLastSign(){
    var last = signsDict[pageNum].pop();
    refreshPdfPage();
}


function saveFilePdf(){
//    console.log(JSON.stringify(signsDict));
//    console.log(csrftoken);
    if (confirm("Are you sure? Process irreverible!") == true) {
        var serializedData = JSON.stringify(
                        {
                            'signs':signsDict, 
                            'file_id'   : fileid, 
                            'protocol'  : protocol,
                            "num_pages" : pdfDoc.numPages
                        });
        data = {
            'data':serializedData,
            'csrfmiddlewaretoken':csrftoken,
        };
        $.ajax({
            type: 'POST',
            // dataType:'json',
            url: url_save,
            data: data,
            success: function (response) {
                // on successfull creating object
                console.log(response);
                if (response.save == true){
                    console.log("reload");
                    setTimeout(function () {
                        location.reload();
                    }, 2000);
                    
                }
            },
            error: function (response) {
                // alert the error if any error occured
                console.log("error ajax: ", response);
            }
        });
    }
}


function removeAllSignsFunc(){
    if (confirm("Are you sure remove? Process irreverible!") == true) {
        var serializedData = JSON.stringify(
                        {
                            'file_id'   : fileid, 
                            'protocol'  : protocol,
                        });
        data = {
            'data':serializedData,
            'csrfmiddlewaretoken':csrftoken,
        };
        $.ajax({
            type: 'POST',
            // dataType:'json',
            url: url_removeAllSigns,
            data: data,
            success: function (response) {
                // on successfull creating object
                console.log(response);
                if (response.remove == true){
                    console.log("reload");
                    setTimeout(function () {
                        location.reload();
                    }, 2000);
                    
                }
            },
            error: function (response) {
                // alert the error if any error occured
                console.log("error ajax: ", response);
            }
        });
    }
}


function zoomin(e){ // disabilitata da implementare
    zoom.value = zoom.value + 0.25; 
    // console.log("zoom in", zoom.value);
    $("#zoom").trigger("change");
}


function zoomout(e){ // disabilitata da implementare
    zoom.value = zoom.value - 0.25; 
    // console.log("zoom out", zoom.value);
    $("#zoom").trigger("change");
}


function changeZoom(e){ // disabilitata da implementare
    scale = e.target.value;
    renderPage(pageNum);
}


window.onload = function() {
  // url         = document.getElementById('filepdf').getAttribute('src');
  // fileid      = document.getElementById('filepdf').getAttribute('fileid');
  // protocol    = document.getElementById('filepdf').getAttribute('protocol');
  
  loadingTask = pdfjsLib.getDocument(url);
  canvas      = document.getElementById('pdf-canvas');
  context     = canvas.getContext('2d');
  drawPdf(loadingTask);
  
  document.getElementById('prev').addEventListener('click', onPrevPage);
  document.getElementById('next').addEventListener('click', onNextPage);
  
  removeLastSign = document.getElementById('delLastSign');
  saveFile       = document.getElementById('savePdf');
  removeAllSigns = document.getElementById('removeAllSigns');
  removeLastSign.addEventListener('click', delLastSign);
  saveFile.addEventListener('click', saveFilePdf);
  removeAllSigns.addEventListener('click', removeAllSignsFunc);
  
  removeLastSign.disabled = true;
  saveFile.disabled = true;
  
  canvas.onmousemove = dragMoveListener;
  canvas.ondblclick = newSign;
  
  
  scale = 1.0;
  // var zoom =  document.getElementById('zoom');
  // zoom.onchange = changeZoom;
  // document.getElementById('zoomin').onclick = zoomin;
  // document.getElementById('zoomout').onclick = zoomout;

  
};

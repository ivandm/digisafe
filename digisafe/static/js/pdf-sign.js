const { degrees, PDFDocument, rgb, StandardFonts } = PDFLib

    var filename = document.getElementById('filepdf').textContent;
    var url = "/document/"+filename;
    var log = console.log;
    // console.log(url);
    var pageRendering = false,
        pageNumPending = null,
        pdfX = null,
        pdfY = null,
        mouseX = null,
        mouseY = null;
        
    
    async function modifyPdf() {
      // Fetch an existing PDF document
      <!-- const url = 'url' -->
      const existingPdfBytes = await fetch(url).then(res => res.arrayBuffer())

      // Load a PDFDocument from the existing PDF bytes
      const pdfDoc = await PDFDocument.load(existingPdfBytes)

      // Embed the Helvetica font
      const helveticaFont = await pdfDoc.embedFont(StandardFonts.Helvetica)

      // Get the first page of the document
      const pages = pdfDoc.getPages()
      const firstPage = pages[0]

      // Get the width and height of the first page
      const { width, height } = firstPage.getSize()

      // Draw a string of text diagonally across the first page
      firstPage.drawText('This text was added with JavaScript!', {
        x: 5,
        y: height / 2 + 300,
        size: 50,
        font: helveticaFont,
        color: rgb(0.95, 0.1, 0.1),
        rotate: degrees(-45),
      })

      const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true });
      document.getElementById('pdf').src = pdfDataUri;
      <!-- const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: false }); -->
      <!-- document.getElementById('pdf').src = "data:image/png;base64, "+pdfDataUri; -->
      document.getElementById('pdf').setAttribute("height", height);
      
      <!-- download the pdf file -->
      // Serialize the PDFDocument to bytes (a Uint8Array)
      <!-- const pdfBytes = await pdfDoc.save() -->
      // Trigger the browser to download the PDF document
      <!-- download(pdfBytes, "filename", "application/pdf"); -->
      Geeks();
    }
    
    
    // Position mouse client
    function dragMoveListener (event) {
        // console.log(canvas);
        mouseX = event.offsetX;
        mouseY = event.offsetY
        
        pdfX = event.offsetX;
        pdfY = document.getElementById('pdf').height-event.offsetY;
        document.getElementById('pdf-posX').textContent = pdfX;
        document.getElementById('pdf-posY').textContent = pdfY;
    }
      
    
    // This example assumes execution from the parent of the the iframe
    function bubbleIframeMouseMove(iframe){
        // Save any previous onmousemove handler
        iframe.contentWindow.name = "pdf-window";
        var existingOnMouseMove = iframe.contentWindow.onmousemove;

        // Attach a new onmousemove listener
        iframe.contentWindow.onmousemove = function(e){
            // Fire any existing onmousemove listener 
            if(existingOnMouseMove) existingOnMouseMove(e);

            // Create a new event for the this window
            var evt = document.createEvent("MouseEvents");

            // We'll need this to offset the mouse move appropriately
            var boundingClientRect = iframe.getBoundingClientRect();

            // Initialize the event, copying exiting event values
            // for the most part
            evt.initMouseEvent( 
                "mousemove", 
                true, // bubbles
                false, // not cancelable 
                window,
                e.detail,
                e.screenX,
                e.screenY, 
                e.clientX + boundingClientRect.left, 
                e.clientY + boundingClientRect.top, 
                e.ctrlKey, 
                e.altKey,
                e.shiftKey, 
                e.metaKey,
                e.button, 
                null // no related element
            );

            // Dispatch the mousemove event on the iframe element
            iframe.dispatchEvent(evt);
            console.log("onmousemove");
        };
        <!-- console.log("bubbleIframeMouseMove"); -->
        <!-- console.log(iframe.contentWindow); -->
        <!-- console.log(iframe.contentWindow.getElementsByTagName("body")[0]); -->
        iframe.contentWindow.window.onmousemove = dragMoveListener;
        
    }

    function Geeks() {
            var iframeID = document.getElementById("pdf");
  
            var iframeCW = (iframeID.contentWindow || iframeID.contentDocument);
  
            if (iframeCW.document){
                iframeCW.document.body.style.border = "25px solid red";
                var pdf = iframeID.contentWindow.document.getElementById("viewer");
                console.log(pdf);
                
            }
            console.log(iframeCW);
        }
        
    window.onload = function() {
        modifyPdf();
        window.name = "Main";
        
        <!-- $('pdf').css('pointer-events', 'none'); -->
        var iframe = document.getElementById('pdf');
        <!-- window.onmousemove = dragMoveListener; -->
        <!-- bindIFrameMousemove(iframe); -->
        // Run it through the function to setup bubbling
        <!-- bubbleIframeMouseMove(iframe); -->
        <!-- console.log(window); -->
        <!-- console.log(window.frames[0].document.getElementsByTagName("body")[0]); -->
        <!-- window.frames[0].document.getElementsByTagName("body")[0].setAttribute("height", "10px"); -->
        <!-- window.frames[0].document.getElementsByTagName("body").onclick = function(){ -->
                <!-- alert("Testing...") -->
        <!-- } -->

    };
/**
 * Created by palmer on 16/03/17.
 */

        function refreshDatasetSelect(){
            $.getJSON($SCRIPT_ROOT + '/_ds/', {})
                    .done(function(data){
                        var options = '';
                        for (var x = 0; x < data.ds_ids.length; x++) {
                            options += '<option value="' + data.ds_ids[x] + '">' + data.ds_names[x] + '</option>';
                        }
                        $('#ds_ids').html(options);
                    })
                    .fail(function(data){console.log('ds fetch failed')})
        }


        function showIonImage(data) {
            var canvas = document.getElementById("ion_image_canvas");
            var ctx = canvas.getContext("2d");
            var background = new Image();
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            background.src = 'data:image/png;base64,' + data.b64_im;
            background.onload = function(){
                // scale up small images to use as much canvas as possible
                ctx.setTransform(1, 0, 0, 1, 0, 0);
                var scale1 = Math.floor(canvas.width / background.width);
                var scale2 = Math.floor(canvas.height / background.height);
                var commonScale = Math.max(1, Math.min(scale1, scale2));
                canvasScaleX = canvasScaleY = commonScale;
                ctx.scale(canvasScaleX, canvasScaleY);

                ctx.drawImage(background, 0, 0);
            }
        }
        function getIonImage() {
                var ds_id = $('select[id="ds_ids"]').val();
                console.log(ds_id);
                var m_z   = $('input[name="m_z"]').val();
                $.getJSON($SCRIPT_ROOT + ds_id + '/im/' + m_z,
                        {
                            ppm: $('input[name="ppm"]').val()
                        })
                        .done(function(data) {
                            $('input[name=a]').focus().select();
                            showIonImage(data);
                        })
                        .fail(function() {
                        console.log( "image fetch failed" );
                        });
                return false;
        }
        function bindGetIonImage(){
            var submit_form = getIonImage;
            $('a#calculate').bind('click', submit_form);
            $('input[type=text]').bind('keydown', function(e) {
                if (e.keyCode == 13) {
                    submit_form;
                }
            });
            $('input[name=a]').focus();
        }

        function bindDatasetSelect(){
            var submit_form = getIonImage;
            $('ds_ids').bind('change', submit_form);
        }

        function showIsotopePattern() {
            var sf = $('input[name="sum_formula"]').val();
            var adduct = $('select[name="adduct_select"]').val();
            console.log([sf, adduct]);
            $.getJSON($SCRIPT_ROOT + '/_isotope/' + sf +"/" + adduct + "/", {resolving_power: $('input[id="resolving_power"]').val()})
                    .done(function(data){
                        addIsotopePlot(data, name="Isotope: " + sf + adduct)
                    })
                    .fail(function() {
                        console.log( "isotope fetch failed" );
                    });

            }

        function addIsotopePlot(data){
            var test = (typeof minmz !== 'undefined') ?  name : '';
            console.log(data.sf);
            // format data
            var spec = parseSpectrumData(data);
            // add named trace to plot
            var plotDiv = document.getElementById("spec_view");
            var intensity = Number($('input[id="isotope_intensity"]').val())/100.; //divide 100 as isopattern returns %
            for (var i=0; i<plotDiv.data.length; i++){
                if (plotDiv.data[i].name == "Isotope:" + data.sf)
                    {
                        Plotly.deleteTraces(plotDiv, i);
                    }
            }
            var traces = [{
                    x: spec[0],
                    y: spec[1].map(function(x) { return x * intensity; }),
                    'name': "Isotope:" + data.sf
                }];
            Plotly.plot(plotDiv, traces);
            Plotly.moveTraces(plotDiv, -1, 0);
        }

        function clearIsotopePattern(){
            var plotData = plotDiv.data;
            var to_delete = [];
            for (var i=0; i<plotData.length; i++){
                if (plotData[i].name.startsWith("Isotope:"))
                    {
                        to_delete.push(i)
                    }
            }
            Plotly.deleteTraces(plotDiv, to_delete);
        }

        function clearSpectrumPlot() {
            var plotData = plotDiv.data;
            var to_delete = [];
            for (var i=0; i<plotData.length; i++){
                console.log(plotData[i].name, plotData[i].name.startsWith("Spectrum"));
                if (plotData[i].name.startsWith("Spectrum"))
                    {
                        console.log('clear trace');
                        to_delete.push(i)
                    }
            }
            Plotly.deleteTraces(plotDiv, to_delete);
        }

        function spectrumZoomHandler(eventdata) {
            console.log( 'ZOOM!' + '\n\n' +
                         'Event data:' + '\n' +
                         JSON.stringify(eventdata) + '\n\n' +
                         'x-axis start:' + eventdata['xaxis.range[0]'] + '\n' +
                         'x-axis end:' + eventdata['xaxis.range[1]'] );
            console.log('update spectrum');
            updateSpectrum({x: c_x, y: c_y},
                           eventdata['xaxis.range[0]'],
                           eventdata['xaxis.range[1]']);
        }

        function parseSpectrumData(json_data){
            var x = [], y = [];
            for (var i = 0; i < json_data.spec.length; i++) {
                row = json_data.spec[i];
                x.push(row[0]);
                y.push(row[1]);
            }
            return [x, y]
        }

        function updateSpectrum(x_y, minmz, maxmz, npeaks){
            var minmz = (typeof minmz !== 'undefined') ?  minmz : null;
            var maxmz = (typeof maxmz !== 'undefined') ?  maxmz : null;
            var npeaks = (typeof npeaks !== 'undefined') ?  npeaks : 500;
            var ds_id = $('select[id="ds_ids"]').val();
            for(var ii=0;ii<spectra_stack.length; ii++){
                console.log(spectra_stack[ii]);
                $.getJSON($SCRIPT_ROOT + ds_id + '/spec_xy/' + spectra_stack[ii].x +"/" + spectra_stack[ii].y + "/",
                    {npeaks: npeaks,
                     minmz: minmz,
                     maxmz: maxmz
                    })
                    .done(function(data) {
                        console.log( "ajax: got spec data" );
                        updateSpectrumPlot(data)
                    })
                    .fail(function() {
                        console.log( "error" );
                    });
            }
        }

        function writeMessage(canvas, message) {
            var context = canvas.getContext('2d');
            context.clearRect(0, 0, canvas.width, canvas.height);
            context.font = '18pt Calibri';
            context.fillStyle = 'black';
            context.fillText(message, 10, 25);
        }

        function getMousePos(evt) {
            var canvas = evt.target,
                rect = canvas.getBoundingClientRect(),
                scaleX = canvas.width / rect.width,
                scaleY = canvas.height / rect.height;
            return {
                x: (evt.clientX - rect.left) * scaleX,
                y: (evt.clientY - rect.top) * scaleY
            };
        }

        function updateSpectrumPlot(json_data){
            var spec = parseSpectrumData(json_data);
            var x = spec[0], y = spec[1];
            var _x = json_data.x; // global - current pixel
            var _y = json_data.y; // global - current pixel
            var traces = [{
                x: x,
                y: y,
                name: 'Spectrum from (' + _x + ' ' + _y + ')',
                line: {
                    //color: 'black'
                }
            }];
            var y_max = Math.max(y);
            var layouts = {
                //title: 'Spectrum from (' + _x + ' ' + _y + ')',
                yaxis: {range: [0, y_max]},
                autosize: false,
                  width: 500,
                  height: 400,
                  margin: {
                    l: 50,
                    r: 10,
                    b: 50,
                    t: 10,
                    pad: 4
                  },
                showlegend: true,
                legend: {
                    x: 0.6,
                    y: 1
                }
            };
            // mark old traces for deletion
            var plotData = plotDiv.data;
            var to_delete = [];
            for (var i=0; i<plotData.length; i++){
                if (plotData[i].name == ('Spectrum from (' + _x + ' ' + _y + ')'))
                {
                    to_delete.push(i)
                }
            }
            Plotly.deleteTraces(plotDiv, to_delete);

            Plotly.plot(plotDiv, traces, layouts);
            console.log('deleting old trace');
        }

        // Put an empty plot into the plotly div
        var c_x = 0, // global  - current pixel
            c_y = 0, // global - current pixel
            plotDiv = document.getElementById("spec_view"),
            spectra_stack = [],
            canvasScaleX = 1,
            canvasScaleY = 1;
        Plotly.plot(plotDiv, [{x:[0], y:[0], name:'Spectrum'}]);
        plotDiv.on('plotly_relayout', spectrumZoomHandler);
        var text = document.getElementById('spec_string');

        function ionImageClickHandler(evt) {
            var mousePos = getMousePos(evt);
            var imgPos = {x: Math.floor(mousePos.x / canvasScaleX),
                          y: Math.floor(mousePos.y / canvasScaleY)}
            //var message = 'Mouse position: ' + mousePos.x + ',' + mousePos.y;
            //writeMessage(canvas_write, message);
            var hold_value = document.getElementById("holdSpectrum").checked;
            if (hold_value){
                spectra_stack.push(imgPos);
                xRange = plotDiv.layout.xaxis.range;
                var min_mz = xRange[0];
                var max_mz = xRange[1];
                updateSpectrum(imgPos, min_mz, max_mz)
            } else {
                console.log('clear spectrum');
                clearSpectrumPlot();
                spectra_stack = [imgPos];
                updateSpectrum(imgPos)
            }
        }
        function getImzmlHeader(){
            var ds_id = $('select[id="ds_ids"]').val();
            window.location.href= ds_id + "/imzml_header/txt"

        }
        function setupCanvas() {
            var canvas = document.getElementById("ion_image_canvas");
            var ctx = canvas.getContext("2d");
            // disable interpolation for scaled images
            ctx.imageSmoothingEnabled = false;
            ctx.webkitImageSmoothingEnabled = false;
            ctx.mozImageSmoothingEnabled = false;
            canvas.addEventListener('mouseup', ionImageClickHandler, false);
        }
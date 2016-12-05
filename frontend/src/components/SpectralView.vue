<template>
  <div id="spectral-view">
    <div ref="container"></div>
    <el-button v-if="spectra.length > 0" @click="onClearClick">Clear spectra</el-button>
  </div>
</template>

<script>
import unzip from 'lodash/unzip';
import Plotly from 'plotly.js/lib/index-basic'
export default {
  name: 'spectral-view',
  props: ['spectra'],
  methods: {
    onClearClick: function() {
      this.$emit('clear');
    }
  },
  watch: {
    spectra: function(data) {
      console.log('redraw');
      var layout = {
        title: "Spectra",
        showlegend: true,
        legend: {x: 0.8, y: 1}
      };
      var traces = [],
          maxIntensity = 0;
      for (var i = 0; i < data.length; i++) {
        if (data[i].peaks.length == 0) {
// http://stackoverflow.com/questions/33112854/plotly-have-trace-without-data-in-legend
          traces.push({
            x: [0], y: [0], name
          });
        } else {
          var spectrum = data[i].peaks;
          var arrays = unzip(spectrum),
              mzs = arrays[0],
              intensities = arrays[1],
              name = data[i].label;
          traces.push({
            x: mzs,
            y: intensities,
            name
          });
          maxIntensity = Math.max(maxIntensity, Math.max(...intensities));
        }
      }
      layout.yaxis = {range: [0, maxIntensity]};
      Plotly.newPlot(this.$refs.container, traces, layout);
      this.$refs.container.on('plotly_relayout', (event) => {
        console.log(event);
        this.$emit('zoom', [event['xaxis.range[0]'] || null,
                            event['xaxis.range[1]'] || null]);
        console.log('zoom');
      });
    }
  }
}
</script>

<style>
</style>

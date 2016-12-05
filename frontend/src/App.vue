<template>
  <div id="app">
    <el-row class="page-header">
      <el-col :span=8>
        <h1><b>IMS data explorer</b></h1>
        <p class="lead">View ion images and spectra from a dataset.</p>
      </el-col>
      <el-col :span=16>
        <settings-form v-on:settingsChange="updateIonImage"></settings-form>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span=12>
        <spatial-view :b64data="ionImageData" v-on:click="updateSpectrum">
        </spatial-view>
      </el-col>
      <el-col :span=12>
        <spectral-view :spectra="spectra"
                       @clear="clearSpectrumPlot"
                       @zoom="zoomSpectralPlot">
        </spectral-view>
      </el-col>
    </el-row>
    <div id="footer">
      &copy; <a href="https://github.com/SpatialMetabolomics/data_serve">Open Source</a>
    </div>
  </div>
</template>

<script>
import SettingsForm from './components/SettingsForm.vue';
import SpatialView from './components/SpatialView.vue';
import SpectralView from './components/SpectralView.vue';

export default {
  name: 'app',
  data () {
    return {
      ionImageData: '',
      selectedPixels: [],
      datasetId: null,
      mzRange: [null, null],
      spectra: [],
      nPeaks: 500
    }
  },

  methods: {
    updateIonImage (settings) {
      this.$resource('{ds_id}/im/{mz}').get({
        ds_id: settings.dataset, mz: settings.mz, ppm: settings.ppm
      }).then(function(response) {
        this.datasetId = settings.dataset;
        this.ionImageData = response.body.b64_im;
      });
    },

    updateSpectrum (position) {
      console.log(`Spectrum position: (${position.x}, ${position.y})`)
      this.selectedPixels.push({datasetId: this.datasetId, x: position.x, y: position.y});

      this.$resource('{dsId}/spec_xy/{x}/{y}/')
        .get({dsId: this.datasetId,
              x: position.x, y: position.y,
              minmz: this.mzRange[0],
              maxmz: this.mzRange[1],
              npeaks: this.nPeaks})
        .then((response) => {
          //this.spectra = [];
          this.spectra.push({
            peaks: response.body.spec,
            label: 'Spectrum from (' + position.x + ', ' + position.y + ')'
          });
        });
    },

    clearSpectrumPlot() {
      this.spectra = [];
      this.selectedPixels = [];
    },

    zoomSpectralPlot(mzRange) {
      console.log(mzRange);
      this.mzRange = mzRange;
      var spectra = [];
      var processed = 0;

      for (let i = 0; i < this.selectedPixels.length; i++) {
        var p = this.selectedPixels[i],
            params = {
              datasetId: p.datasetId, x: p.x, y: p.y,
              minmz: this.mzRange[0],
              maxmz: this.mzRange[1],
              npeaks: this.nPeaks
            };
        this.$resource('{datasetId}/spec_xy/{x}/{y}/')
          .get(params).then((response) => {
            spectra[i] = {
              peaks: response.body.spec,
              label: 'Spectrum from (' + params.x + ', ' + params.y + ')'
            };
            ++processed;

            if (processed == this.selectedPixels.length)
              this.spectra = spectra;
          });
      }
    }
  },

  components: {
    SettingsForm,
    SpatialView,
    SpectralView
  },
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

.page-header {
  text-shadow: 2px 2px 3px #a5a8a5;
  text-align: left;
  margin-bottom: 10px;
  background: linear-gradient(180deg, #cef, #fff);
  font-family: 'sans-serif';
}

.lead {
  color: grey;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>

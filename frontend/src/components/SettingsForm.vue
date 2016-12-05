<template>
  <div id="spatial-view">
    <el-form :inline="true">
      <el-form-item>
        <el-select v-model="query.dataset" placeholder="Dataset ID" :disabled="!datasetList">
          <el-option
              v-for="(name, id) in datasetList"
              :label="name" :value="id" :title="id">
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="m/z" label-width="30px">
        <el-input-number v-model="query.mz" :min=10 :max=10000 :step=0.001
                          @keyup.enter.native="submit" size="small">
        </el-input-number>
      </el-form-item>

      <el-form-item label="ppm" label-width="30px">
        <el-input-number v-model="query.ppm" :min=1 :max=10
                          @keyup.enter.native="submit" size="small">
        </el-input-number>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submit" :disabled='!query.dataset'>
          Get image
        </el-button>
      </el-form-item>

    </el-form>
  </div>
</template>

<script>
import fromPairs from 'lodash/fromPairs'
import zip from 'lodash/zip'

export default {
  name: 'settings-form',
  data () {
    return {
      datasetList: [],
      query: {
        dataset: '',
        mz: 300,
        ppm: 6
      }
    }
  },
  methods: {
    submit: function() {
      this.$emit('settingsChange', this.query);
    }
  },
  mounted () {
    this.$http.get('_ds/').then(function (response) {
      var json = response.data;
      console.log(json);
      // dictionary ID -> name
      this.datasetList = fromPairs(zip(json.ds_ids, json.ds_names))
    }, function (response) { console.log(response) })
  }
}
</script>

<style>
  #spatial-view {
  margin-top: 1em;
  }
</style>

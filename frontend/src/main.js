import Vue from 'vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-default/index.css'
import locale from 'element-ui/lib/locale/lang/en'
import App from './App.vue'

// Like Bootstrap but native for Vue
Vue.use(ElementUI, { locale })
Vue.use(require('vue-resource'))

// local host:port of Flask REST API
Vue.http.options.root = "http://localhost:9414";

// change the delimiters to avoid conflict with Flask
Vue.config.delimiters = ["${", "}"];

new Vue({
    el: '#app',
    render: h => h(App)
})

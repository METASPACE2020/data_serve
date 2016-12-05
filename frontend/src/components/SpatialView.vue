<template>
  <div id="spatial-view">
    <canvas class="ion-image" ref="canvas" width="500px" height="800px"
            @click="clickHandler">
    </canvas>
  </div>
</template>

<script>
export default {
  name: 'spatial-view',
  props: ['b64data'],
  data () {
    return {
      scaleFactor: 1
    }
  },

  mounted () {
    var canvas = this.$refs.canvas;
    var ctx = canvas.getContext("2d");
    // disable interpolation for scaled images
    ctx.imageSmoothingEnabled = false;
    ctx.webkitImageSmoothingEnabled = false;
    ctx.mozImageSmoothingEnabled = false;
  },

  methods: {
    clickHandler (evt) {
      var canvas = evt.target,
          rect = canvas.getBoundingClientRect(),
          scaleX = canvas.width / rect.width,
          scaleY = canvas.height / rect.height,
          mousePos = {
            x: (evt.clientX - rect.left) * scaleX,
            y: (evt.clientY - rect.top) * scaleY
          };

      this.$emit('click', {x: Math.floor(mousePos.x / this.scaleFactor),
                           y: Math.floor(mousePos.y / this.scaleFactor)})
    }
  },

  watch: {
    b64data: function(data) {
      var canvas = this.$refs.canvas;
      var ctx = canvas.getContext("2d");
      var background = new Image();

      // clear previous contents
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      background.src = 'data:image/png;base64,' + data;
      background.onload = () => {
        // reset the scaling
        ctx.setTransform(1, 0, 0, 1, 0, 0);

        // scale up small images to use as much canvas as possible
        var scale1 = Math.floor(canvas.width / background.width);
        var scale2 = Math.floor(canvas.height / background.height);
        this.scaleFactor = Math.max(1, Math.min(scale1, scale2));
        ctx.scale(this.scaleFactor, this.scaleFactor);

        ctx.drawImage(background, 0, 0);
      }
    }
  }
}
</script>

<style>
.ion-image:hover {
  cursor: crosshair;
}
</style>

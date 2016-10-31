/* globals Chartist */
// Started as https://github.com/gionkunz/chartist-plugin-pointlabels
(function (window, document, Chartist) {
  var defaultOptions = {
    labelClass: 'ct-label',
    labelOffset: {
      x: 0,
      y: -10
    },
    textAnchor: 'middle',
    labelInterpolationFnc: function (value) {
      return value
    }
  }

  Chartist.plugins = Chartist.plugins || {}
  Chartist.plugins.ctPointLabels = function (options) {
    options = Chartist.extend({}, defaultOptions, options)

    return function ctPointLabels (chart) {
      chart.on('draw', function (data) {
        if (data.type === 'point') {
          data.group.elem('text', {
            x: data.x + options.labelOffset.x,
            y: data.y + options.labelOffset.y,
            style: 'text-anchor: ' + options.textAnchor
          }, options.labelClass).text(options.labelInterpolationFnc(data.value.x === undefined ? data.value.y : data.value.x + ', ' + data.value.y))
        } else if (data.type === 'bar') {
          data.group.elem('text', {
            x: data.x2 + options.labelOffset.x,
            y: data.y2 + options.labelOffset.y,
            style: 'text-anchor: ' + options.textAnchor
          }, options.labelClass).text(options.labelInterpolationFnc(data.value.x === undefined ? data.value.y : data.value.x + ', ' + data.value.y))
        }
      })
    }
  }
}(window, document, Chartist))

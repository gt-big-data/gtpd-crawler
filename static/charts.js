/* globals Chartist, XMLHttpRequest */

// Global options to make Charist charts better for us.
var lineOptions = {
  lineSmooth: false,
  axisY: {
    showLabel: false
  },
  plugins: [
    Chartist.plugins.ctPointLabels()
  ],
  fullWidth: true
}

var barOptions = {
  axisY: {
    showLabel: false
  },
  plugins: [
    Chartist.plugins.ctPointLabels()
  ],
  fullWidth: true
}

function getData (jsonUrl, cb) {
  var request = new XMLHttpRequest()
  request.onreadystatechange = function () {
    if (request.readyState === 4 && request.status === 200) {
      var data = JSON.parse(request.responseText)
      cb(data)
    }
  }
  request.open('GET', jsonUrl, true)
  request.overrideMimeType('application/json')
  request.send()
}

function showChartTotal (data) {
  console.log(data)
  var labels = ['Non Criminal', 'Criminal']
  var series = [data['non_criminal_count'], data['criminal_count']]

  var chartData = {
    labels: labels,
    series: [series]
  }
  console.log(chartData)
  new Chartist.Bar('#chart-crimes-total', chartData, barOptions)
}

getData('/api/total', showChartTotal)

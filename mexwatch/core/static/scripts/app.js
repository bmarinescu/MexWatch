var fillsChart = d3.select('#fills-chart'),
    margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = +fillsChart.attr("width") - margin.left - margin.right,
    height = +fillsChart.attr("height") - margin.top - margin.bottom,
    g = fillsChart.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")"),
    x = d3.scaleTime().range([0, width]),
    y = d3.scaleLinear().range([height, 0]);

(function ($) {
    var user = window.location.pathname.replace('/u/', '');

    getCharts();

    //get charts
    function getCharts() {
        $.ajax({
            method: 'GET',
            url: '/api/charts',
            success: function (response) {
                $.each(response.charts, function (index, chart) {
                    getChartData(user, chart);
                });
            }
        });
    }

    console.log("aa");

    function getChartData(user, chart) {
        $.ajax({
            method: 'GET',
            url: '/api/chart_data',
            data: {
                username: user,
                chart_name: chart
            },
            success: function (response) {
            }
        });
    }


    //add charts
    $('body').on('click', 'button.add-chart', function () {
        var chart = $('div.base-chart').clone();

        chart.insertAfter($(this).closest('div.chart-container')).removeClass('base-chart hide');

        return false;
    });

    //delete charts
    $('body').on('click', 'button.delete-chart', function () {
        var c = confirm("Are you sure you want to delete this chart?");

        if (c) {
            $(this).closest('div.chart-container').fadeOut(500, function () {
                $(this).remove();
            });
        }

        return false;
    });
})(jQuery);


function showChart(data) {

    // var data = walletHistory;

    //setup variables
    var margin = {top: 20, right: 20, bottom: 100, left: 50},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom,
        svg = d3.select('#chart').attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")"),
        parseTime = d3.timeParse("%Y-%m-%dT%H:%M:%S"),
        x = d3.scaleTime().range([0, width]),
        y = d3.scaleLinear().range([height, 0]),
        valueline = d3.line()
            .x(function (d) {
                return x(d.date);
            })
            .y(function (d) {
                return y(d.value);
            }),
        tooltip = d3.select("body").append("div")
            .attr("class", "d3-tooltip")
            .style("opacity", 0);

    //parse the date
    data.forEach(function (d) {
        d.date = d.timestamp && parseTime(d.timestamp.split('.')[0]);
    });

    // scale the range of the data
    x.domain(d3.extent(data, function (d) {
        return d.date;
    }));

    y.domain(d3.extent(data, function (d) {
        d.value = d.value / 100000000;
        return d.value;
    }));

    // add the valueline path.
    svg.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", valueline);

    // Add the scatterplot
    svg.selectAll("dot")
        .data(data)
        .enter().append("circle")
        .attr('class', 'dot')
        .attr("r", 3.5)
        .attr("cx", function (d) {
            return x(d.date);
        })
        .attr("cy", function (d) {
            return y(d.value);
        })
        .on("mouseover", function (d) {
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);

            tooltip.html(
                "Type: " + d.transactType + "<br/>" +
                "Status: " + d.transactStatus + "<br/>" +
                "Date: " + d.timestamp + "<br/>" +
                "Value: " + d.value + "<br />" +
                "Amount: " + d.amount + " " + d.currency
            )
                .style("left", (d3.event.pageX + 10) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function (d) {
            tooltip.transition()
                .duration(200)
                .style("opacity", 0);
        });


    // add the X Axis
    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%Y-%m-%d")))
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");

    // add the Y Axis
    svg.append("g")
        .attr("class", "axis")
        .call(d3.axisLeft(y));
}

window.onload = function() {
    console.log("Window loaded, initializing chart...");
    
    var options = {
        series: [44, 55, 41, 17, 15],
        chart: {
            type: 'donut',
        },
        responsive: [{
            breakpoint: 768,
            options: {
                chart: {
                    width: 200
                },
                legend: {
                    position: 'bottom'
                }
            }
        }]
    };

    var chartElement = document.querySelector("#Donut");
   
    if (chartElement) {
        var chart = new ApexCharts(chartElement, options);
        chart.render();
    } else {
        console.error("Element not found");
    }
};
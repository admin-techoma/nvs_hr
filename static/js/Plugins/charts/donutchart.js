// window.onload = function() {
    
//     var options = {
//         series: [44, 55, 41, 17, 15],
//         chart: {
//             type: 'donut',
//         },
//         responsive: [{
//             breakpoint: 768,
//             options: {
//                 chart: {
//                     width: 200
//                 },
//                 legend: {
//                     position: 'bottom'
//                 }
//             }
//         }]
//     };

//     var chartElement = document.querySelector("#Donut");
   
//     if (chartElement) {
//         var chart = new ApexCharts(chartElement, options);
//         chart.render();
//     } else {
//         console.error("Element not found");
//     }
// };

document.addEventListener('DOMContentLoaded', function() {
    var options = {
        chart: {
            type: 'donut'
        },
        series: [ 55, 41,],
        labels: ['Active', 'On Leave'],
        fill: { color: ['#5FFF9F', '#ff2f2f'] } 
    };

    var chart = new ApexCharts(document.querySelector("#Donut"), options);

    chart.render().catch(function(e) {
        console.error("Error rendering chart:", e);
    });
});
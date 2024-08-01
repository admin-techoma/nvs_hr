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
        series: [44, 55, 41, 17, 15],
        labels: ['Apple', 'Mango', 'Orange', 'Watermelon', 'Pineapple']
    };

    var chart = new ApexCharts(document.querySelector("#Donut"), options);

    chart.render().catch(function(e) {
        console.error("Error rendering chart:", e);
    });
});
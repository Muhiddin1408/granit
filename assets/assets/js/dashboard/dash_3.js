try {

    $(document).ready(function () {
        $.ajax({
        url: '/chart-savdo-tahlil/',
        success: function (data) {
            console.log(data)
            var d_1options1 = {
                chart: {
                    height: 350,
                    type: 'bar',
                    toolbar: {
                    show: false,
                    }
                },
                colors: ['#5c1ac3', '#d6b007'],
                plotOptions: {
                    bar: {
                        horizontal: false,
                        columnWidth: '55%',
                        endingShape: 'rounded'  
                    },
                },
                dataLabels: {
                    enabled: false
                },
                legend: {
                    position: 'bottom',
                    horizontalAlign: 'center',
                    fontSize: '14px',
                    markers: {
                        width: 10,
                        height: 10,
                    },
                    itemMargin: {
                        horizontal: 0,
                        vertical: 8
                    }
                },
                stroke: {
                    show: true,
                    width: 2,
                    colors: ['transparent']
                },
                series: [{
                    name: 'Sotuv summasi',
                    data: data.total_income
                }, {
                name: 'Yalpi daromad',
                data: data.yalpi_daromad
                }],
                xaxis: {
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                },
                fill: {
                type: 'gradient',
                gradient: {
                    shade: 'light',
                    type: 'vertical',
                    shadeIntensity: 0.3,
                    inverseColors: false,
                    opacityFrom: 1,
                    opacityTo: 0.8,
                    stops: [0, 100]
                }
                },
                tooltip: {
                    y: {
                        formatter: function (val) {
                            return val
                        }
                    }
                }
            }
        
            var d_1C_3 = new ApexCharts(
                document.querySelector("#uniqueVisits"),
                d_1options1
            );
            d_1C_3.render();

          }
        });
    });

  } catch(e) {
  // statements
  console.log(e);
  }
  
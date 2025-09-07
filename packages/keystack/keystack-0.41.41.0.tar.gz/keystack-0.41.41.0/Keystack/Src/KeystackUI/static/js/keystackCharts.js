/* import Chart from '/opt/Keystack_src/KeystackUI/base/static/Chart.js/auto'; */
/* const { Chart } = await import('/opt/Keystack_src/KeystackUI/base/static/Chart.js/dist/chart.umd.js'); */
/* import {Chart} from "/opt/Keystack_src/KeystackUI/base/static/Chart.js/dist/chart.umd.js"; */
/* import {Chart} from "/opt/Keystack_src/KeystackUI/base/static/Chart.js/dist/auto"; */

function showCharts() {
    const data = [
    { year: 2010, count: 10 },
    { year: 2011, count: 20 },
    { year: 2012, count: 15 },
    { year: 2013, count: 25 },
    { year: 2014, count: 22 },
    { year: 2015, count: 30 },
    { year: 2016, count: 28 },
    ];

    new Chart(
        document.querySelector('#acquisitions'),
        {
            type: 'bar',
            data: {
                labels: data.map(row => row.year),
                datasets: [
                    {
                    label: 'Acquisitions by year',
                    data: data.map(row => row.count)
                   }
                ]
            }
        }
    );
}
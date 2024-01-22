<script setup>
import Chart from 'chart.js/auto'
import 'chartjs-adapter-date-fns'

const { params } = useRoute()

const sensor = params.sensor ? params.sensor.charAt(0).toUpperCase() + params.sensor.slice(1) : null
const days = params.days ? parseInt(params.days) : 30
const currentDate = new Date()
const startDate = new Date(currentDate)
startDate.setDate(currentDate.getDate() - days)

const apiUrl = `https://api.roots.ee/inkbird?sensor=${sensor}&start=${startDate.toISOString().substring(0, 10)}&end=${currentDate.toISOString().substring(0, 10)}`
const chartOptions = {
  spanGaps: 1000 * 60 * 60 * 24,
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'nearest'
  },
  scales: {
    x: {
      type: 'time',
      display: true,
      time: {
        unit: 'hour',
        displayFormats: {
          hour: 'HH:mm',
          day: 'd. MMM'
        }
      },
      title: {
        display: false
      },
      ticks: {
        autoSkip: false,
        maxRotation: 0,
        major: {
          enabled: true
        },
        font: function (context) {
          if (context.tick && context.tick.major) {
            return {
              weight: 'bold'
            }
          }
        }
      }
    },
    y: {
      title: {
        display: true,
        text: 'Temperature (°C)'
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        title: context => formatDateFromTimestamp(context.at(0).parsed.x)
      }
    }
  }
}

const temperatureChart = ref(null)
const humidityChart = ref(null)

onMounted(async () => {
  const response = await fetch(apiUrl)

  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`)
  }

  const data = await response.json()

  // Assuming the first row of the data contains headers ["Date", "Temperature", "Humidity"]
  const headers = data.at(0)
  const dateIndex = headers.indexOf('Date')
  const temperatureIndex = headers.indexOf('Temperature')
  const humidityIndex = headers.indexOf('Humidity')

  // Extract data excluding the header row
  const rowData = data.slice(1)

  // Extracting specific columns for chart rendering
  const labels = rowData.map(row => formatDateTimeZone(row[dateIndex]))
  const temperatureData = rowData.map(row => row[temperatureIndex])
  const humidityData = rowData.map(row => row[humidityIndex])

  renderTemperatureChart(labels, temperatureData)
  renderHumidityChart(labels, humidityData)
})

function renderTemperatureChart (labels, temperatureData) {
  const ctx = temperatureChart.value.getContext('2d')
  chartOptions.scales.y.title.text = 'Temperature (°C)'

  const c = new Chart(ctx, {
    data: {
      labels,
      datasets: [
        {
          label: 'Temperature (°C)',
          data: temperatureData,
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 2,
          cubicInterpolationMode: 'monotone',
          fill: false,
          pointStyle: false
        }
      ]
    },
    options: chartOptions,
    type: 'line'
  })
}

function renderHumidityChart (labels, humidityData) {
  const ctx = humidityChart.value.getContext('2d')
  chartOptions.scales.y.title.text = 'Humidity (%)'

  const c = new Chart(ctx, {
    data: {
      labels,
      datasets: [
        {
          label: 'Humidity (%)',
          data: humidityData,
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 2,
          cubicInterpolationMode: 'monotone',
          fill: false,
          pointStyle: false
        }
      ]
    },
    options: chartOptions,
    type: 'line'
  })
}

function formatDateTimeZone (dateString) {
  const date = new Date(dateString)
  const tallinnDate = new Date(date.toLocaleString('en-US', { timeZone: 'Europe/Tallinn' }))

  const utcDate = Date.UTC(
    tallinnDate.getUTCFullYear(),
    tallinnDate.getUTCMonth(),
    tallinnDate.getUTCDate(),
    tallinnDate.getUTCHours(),
    tallinnDate.getUTCMinutes(),
    tallinnDate.getUTCSeconds()
  )

  return new Date(utcDate)
}

function formatDateFromTimestamp (timestamp) {
  return new Date(timestamp).toLocaleString('et', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="h-full w-full py-8 md:p-8 flex flex-col gap-16">
    <h1 class="text-center text-lg font-extrabold">
      {{ sensor }}
      <span class="block text-sm font-thin">last {{ days }} days</span>
    </h1>
    <div class="h-1/2">
      <canvas ref="temperatureChart" />
    </div>
    <div class="h-1/2">
      <canvas ref="humidityChart" />
    </div>
  </div>
</template>

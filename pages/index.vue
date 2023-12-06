<script setup>
import Chart from 'chart.js/auto'

const temperatureChart = ref(null)
const humidityChart = ref(null)
const apiUrl = 'https://api.roots.ee/inkbird?sensor=Storage&start=2023-12-01&end=2024-01-01'

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
  const labels = rowData.map(row => formatDateAsTimestamp(row[dateIndex]))
  const temperatureData = rowData.map(row => row[temperatureIndex])
  const humidityData = rowData.map(row => row[humidityIndex])

  const minTimestamp = Math.min(...labels)
  const maxTimestamp = Math.max(...labels)

  renderTemperatureChart(labels, temperatureData, minTimestamp, maxTimestamp)
  renderHumidityChart(labels, humidityData, minTimestamp, maxTimestamp)
})

const renderTemperatureChart = (labels, temperatureData, minTimestamp, maxTimestamp) => {
  const ctx = temperatureChart.value.getContext('2d')

  return new Chart(ctx, {
    type: 'line',
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
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: 'linear',
          position: 'bottom',
          ticks: {
            callback: value => formatDateFromTimestamp(value),
            min: minTimestamp,
            max: maxTimestamp
          }
        },
        y: {
          beginAtZero: true,
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
            title: context => formatDateFromTimestamp(context.at(0).parsed.x),
            label: context => `${context.parsed.y}°C`
          }
        }
      }
    }
  })
}

const renderHumidityChart = (labels, humidityData, minTimestamp, maxTimestamp) => {
  const ctx = humidityChart.value.getContext('2d')

  return new Chart(ctx, {
    type: 'line',
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
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: 'linear',
          position: 'bottom',
          ticks: {
            callback: value => formatDateFromTimestamp(value),
            min: minTimestamp,
            max: maxTimestamp
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Humidity (%)'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            title: context => formatDateFromTimestamp(context.at(0).parsed.x),
            label: context => `${context.parsed.y}%`
          }
        }
      }
    }
  })
}

const formatDateAsTimestamp = (dateTimeString) => {
  return new Date(dateTimeString).getTime()
}

const formatDateFromTimestamp = (timestamp) => {
  return new Date(timestamp)
    .toISOString()
    .replace(/T/, ' ')
    .replace(/\..+/, '')
    .substring(0, 16)
}
</script>

<template>
  <div class="h-full w-full p-16 flex flex-col gap-16">
    <div class="h-1/2">
      <canvas ref="temperatureChart" />
    </div>
    <div class="h-1/2">
      <canvas ref="humidityChart" />
    </div>
  </div>
</template>

import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js';

ChartJS.register(ArcElement, Tooltip);

/** Tương đương renderDoughnutChart() trong student-dashboard.js cũ */
// Biểu đồ vòng: phần đã hoàn thành / phần còn lại
export default function ProgressDoughnut({ completed, total }) {
  const rem = Math.max(0, total - completed);

  const data = {
    labels: ['Hoàn thành', 'Còn lại'],
    datasets: [
      {
        data: [completed, rem],
        backgroundColor: ['#2563EB', '#E2E8F0'],
        borderWidth: 0,
        hoverOffset: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '72%',
    plugins: { legend: { display: false } },
  };

  return <Doughnut data={data} options={options} />;
}

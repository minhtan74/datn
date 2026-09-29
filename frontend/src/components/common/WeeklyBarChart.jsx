import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
} from 'chart.js';

// Đăng ký các thành phần Chart.js cần cho biểu đồ cột
ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

/** Tương đương renderWeeklyChart() trong student-dashboard.js cũ */
// Biểu đồ cột số bài hoàn thành theo ngày (data/labels không truyền thì dùng số liệu mẫu)
export default function WeeklyBarChart({ data, labels }) {
  const chartData = {
    labels: labels || ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
    datasets: [
      {
        label: 'Bài học hoàn thành',
        data: data || [2, 4, 3, 5, 2, 6, 1],
        backgroundColor: 'rgba(37,99,235,0.18)',
        borderColor: '#2563EB',
        borderWidth: 2,
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,.05)' }, ticks: { stepSize: 1 } },
      x: { grid: { display: false } },
    },
  };

  return <Bar data={chartData} options={options} />;
}

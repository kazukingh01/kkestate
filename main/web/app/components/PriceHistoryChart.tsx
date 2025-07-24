import { ClientOnly } from "~/components/ClientOnly";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ComposedChart,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { ja } from 'date-fns/locale';

interface PriceHistoryItem {
  timestamp: string;
  price: number | null;
  min_price: number | null;
  max_price: number | null;
  unit: string | null;
  run_id: number;
  period: number | null;
}

interface PriceHistoryChartProps {
  data: PriceHistoryItem[];
}

function ChartComponent({ data }: PriceHistoryChartProps) {

  // データの前処理
  const chartData = data
    .filter(item => item.price !== null && item.price > 0) // 有効な価格のみ
    .map(item => ({
      date: item.timestamp,
      price: item.price,
      min_price: item.min_price,
      max_price: item.max_price,
      unit: item.unit,
      run_id: item.run_id,
      period: item.period,
      // 表示用の日付フォーマット
      displayDate: format(parseISO(item.timestamp), 'yyyy/MM/dd', { locale: ja }),
    }))
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()); // 日付順にソート

  if (chartData.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>価格データがありません</p>
      </div>
    );
  }

  // Y軸の範囲計算（min/maxも含める）
  const allPrices: number[] = [];
  chartData.forEach(d => {
    if (d.price !== null) allPrices.push(d.price);
    if (d.min_price !== null) allPrices.push(d.min_price);
    if (d.max_price !== null) allPrices.push(d.max_price);
  });
  
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const padding = (maxPrice - minPrice) * 0.1;
  const yAxisMin = Math.max(0, minPrice - padding);
  const yAxisMax = maxPrice + padding;

  // 価格フォーマット関数
  const formatPrice = (value: number) => {
    if (value >= 10000) {
      return `${(value / 10000).toFixed(1)}億円`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(0)}千万円`;
    } else {
      return `${value}万円`;
    }
  };

  // ツールチップ用の価格フォーマット関数（丸めない）
  const formatPriceExact = (value: number) => {
    return `${value}万円`;
  };

  // カスタムツールチップ
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm text-gray-600">{data.displayDate}</p>
          <p className="text-lg font-semibold text-blue-600">
            💰 {formatPriceExact(data.price)}
          </p>
          {data.min_price !== null && data.max_price !== null && (
            <p className="text-sm text-gray-700">
              📊 範囲: {formatPriceExact(data.min_price)} 〜 {formatPriceExact(data.max_price)}
            </p>
          )}
          {data.period !== null && (
            <p className="text-xs text-purple-600">Period: {data.period}</p>
          )}
          <p className="text-xs text-gray-500">Run ID: {data.run_id}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%' }}>
      {/* 統計情報 */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: '20px', 
        marginBottom: '32px'
      }}>
        <div style={{ 
          backgroundColor: '#eff6ff', 
          borderRadius: '12px', 
          padding: '20px', 
          textAlign: 'center',
          border: '2px solid #dbeafe'
        }}>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>💰 最新価格</p>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#2563eb' }}>
            {formatPriceExact(chartData[chartData.length - 1].price)}
          </p>
          {chartData[chartData.length - 1].min_price !== null && chartData[chartData.length - 1].max_price !== null && (
            <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
              範囲: {formatPriceExact(chartData[chartData.length - 1].min_price)} 〜 {formatPriceExact(chartData[chartData.length - 1].max_price)}
            </p>
          )}
        </div>
        <div style={{ 
          backgroundColor: '#f0fdf4', 
          borderRadius: '12px', 
          padding: '20px', 
          textAlign: 'center',
          border: '2px solid #dcfce7'
        }}>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>📈 最高価格</p>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#16a34a' }}>
            {formatPriceExact(maxPrice)}
          </p>
        </div>
        <div style={{ 
          backgroundColor: '#fef2f2', 
          borderRadius: '12px', 
          padding: '20px', 
          textAlign: 'center',
          border: '2px solid #fecaca'
        }}>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>📉 最低価格</p>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc2626' }}>
            {formatPriceExact(minPrice)}
          </p>
        </div>
      </div>

      {/* チャート */}
      <div style={{ 
        height: '400px', 
        backgroundColor: '#fafafa', 
        borderRadius: '12px', 
        padding: '20px',
        border: '1px solid #e5e7eb'
      }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 60,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="displayDate"
              tick={{ fontSize: 12, fill: '#6b7280' }}
              angle={-45}
              textAnchor="end"
              height={80}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[yAxisMin, yAxisMax]}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={formatPrice}
              width={100}
            />
            <Tooltip content={<CustomTooltip />} />
            
            {/* 価格範囲エリア（min-max） */}
            <Area
              type="monotone"
              dataKey="max_price"
              stroke="none"
              fill="#dbeafe"
              fillOpacity={0.4}
            />
            <Area
              type="monotone"
              dataKey="min_price"
              stroke="none"
              fill="#ffffff"
              fillOpacity={1}
            />
            
            {/* 中央値ライン */}
            <Line
              type="monotone"
              dataKey="price"
              stroke="#2563eb"
              strokeWidth={3}
              dot={{ fill: '#2563eb', strokeWidth: 2, r: 5 }}
              activeDot={{ r: 8, stroke: '#2563eb', strokeWidth: 3, fill: '#ffffff' }}
            />
            
            {/* min/maxライン */}
            <Line
              type="monotone"
              dataKey="min_price"
              stroke="#ef4444"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="max_price"
              stroke="#10b981"
              strokeWidth={1}
              strokeDasharray="5 5"  
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* データポイント数表示 */}
      <div style={{ 
        marginTop: '24px', 
        textAlign: 'center', 
        fontSize: '14px', 
        color: '#6b7280',
        padding: '16px',
        backgroundColor: '#f8fafc',
        borderRadius: '8px'
      }}>
        <p style={{ marginBottom: '4px' }}>
          📊 記録期間: {chartData.length}回のデータポイント
        </p>
        <p>
          {format(parseISO(chartData[0].date), 'yyyy年MM月dd日', { locale: ja })} 〜{' '}
          {format(parseISO(chartData[chartData.length - 1].date), 'yyyy年MM月dd日', { locale: ja })}
        </p>
      </div>
    </div>
  );
}

export default function PriceHistoryChart({ data }: PriceHistoryChartProps) {
  return (
    <ClientOnly fallback={
      <div className="text-center py-8 text-gray-500">
        <p>チャートを読み込み中...</p>
      </div>
    }>
      <ChartComponent data={data} />
    </ClientOnly>
  );
}
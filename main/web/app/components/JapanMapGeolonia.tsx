import { useEffect, useState } from 'react';

// 都道府県データの型定義
interface PrefectureData {
  [prefectureCode: string]: {
    name: string;
    count: number;
  };
}

interface JapanMapGeoloniaProps {
  onPrefectureClick: (prefecture: { id: string; name: string }) => void;
  prefectureData: PrefectureData;
}

export default function JapanMapGeolonia({ 
  onPrefectureClick, 
  prefectureData 
}: JapanMapGeoloniaProps) {
  const [svgContent, setSvgContent] = useState<string>("");
  const [hoveredPrefecture, setHoveredPrefecture] = useState<string | null>(null);

  useEffect(() => {
    // SVGファイルを読み込み
    console.log("Starting SVG fetch...");
    fetch("/data/map-mobile.svg")
      .then((res) => {
        console.log("SVG fetch response:", res.status);
        return res.text();
      })
      .then((svg) => {
        console.log("SVG loaded, length:", svg.length);
        setSvgContent(svg);
      })
      .catch((err) => {
        console.error("Failed to load SVG:", err);
        setSvgContent("<p>SVG読み込み失敗</p>");
      });
  }, []);

  // 動的な閾値計算（useEffectの外で実行）
  const counts = Object.values(prefectureData).map(data => data.count).filter(count => count > 0);
  const maxCount = Math.max(...counts, 0);
  const minCount = Math.min(...counts, 0);
  
  // 四分位数を計算
  const sortedCounts = counts.sort((a, b) => a - b);
  const q1 = sortedCounts[Math.floor(sortedCounts.length * 0.25)] || 0;
  const q3 = sortedCounts[Math.floor(sortedCounts.length * 0.75)] || 0;
  const median = sortedCounts[Math.floor(sortedCounts.length * 0.5)] || 0;

  // 都道府県コードから都道府県名へのマッピング
  const codeToNameMap: { [key: string]: string } = {
    '01': 'hokkaido', '02': 'aomori', '03': 'iwate', '04': 'miyagi', '05': 'akita',
    '06': 'yamagata', '07': 'fukushima', '08': 'ibaraki', '09': 'tochigi', '10': 'gumma',
    '11': 'saitama', '12': 'chiba', '13': 'tokyo', '14': 'kanagawa', '15': 'niigata',
    '16': 'toyama', '17': 'ishikawa', '18': 'fukui', '19': 'yamanashi', '20': 'nagano',
    '21': 'gifu', '22': 'shizuoka', '23': 'aichi', '24': 'mie', '25': 'shiga',
    '26': 'kyoto', '27': 'osaka', '28': 'hyogo', '29': 'nara', '30': 'wakayama',
    '31': 'tottori', '32': 'shimane', '33': 'okayama', '34': 'hiroshima', '35': 'yamaguchi',
    '36': 'tokushima', '37': 'kagawa', '38': 'ehime', '39': 'kochi', '40': 'fukuoka',
    '41': 'saga', '42': 'nagasaki', '43': 'kumamoto', '44': 'oita', '45': 'miyazaki',
    '46': 'kagoshima', '47': 'okinawa'
  };

  console.log('[JapanMap] Thresholds:', { q1, median, q3, counts: counts.length });
  console.log('[JapanMap] Prefecture data keys:', Object.keys(prefectureData));

  // 物件数に基づく色分け（動的閾値）
  const getColorByCount = (count: number): string => {
    const color = count === 0 ? '#e5e7eb' :
                  count >= q3 ? '#dc2626' :
                  count >= median ? '#f59e0b' :
                  count >= 1 ? '#10b981' : '#e5e7eb';
    console.log(`[JapanMap] getColorByCount: count=${count}, color=${color}`);
    return color;
  };

  // ホバー時の色
  const getHoverColor = (count: number): string => {
    if (count === 0) return '#d1d5db';     // 濃いグレー
    if (count >= q3) return '#b91c1c';     // 濃い赤
    if (count >= median) return '#d97706'; // 濃いオレンジ
    if (count >= 1) return '#059669';      // 濃い緑
    return '#d1d5db';                      // 濃いグレー
  };

  useEffect(() => {
    if (!svgContent) return;

    // SVGを動的に挿入
    const container = document.getElementById('japan-map-container');
    if (container) {
      container.innerHTML = svgContent;
      
      // SVGのサイズを調整
      const svg = container.querySelector('svg');
      if (svg) {
        svg.style.width = 'auto';
        svg.style.height = 'auto';
        svg.style.maxWidth = '100%';
        svg.style.maxHeight = '100%';
        svg.style.objectFit = 'contain';
        svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
        svg.setAttribute('viewBox', '0 0 1000 1000');
        
      }
      
      // 各都道府県にイベントリスナーを追加
      const prefectures = container.querySelectorAll('g[data-code]');
      console.log(`[JapanMap] Found ${prefectures.length} prefecture elements`);
      
      prefectures.forEach((prefecture) => {
        const element = prefecture as SVGElement;
        const prefCode = element.getAttribute('data-code');
        
        if (prefCode) {
          // データに基づいて色を設定
          const prefectureName = codeToNameMap[prefCode];
          const data = prefectureData[prefectureName];
          const count = data?.count || 0;
          const color = getColorByCount(count);
          console.log(`[JapanMap] Prefecture ${prefCode} (${prefectureName}): count=${count}, color=${color}, data=`, data);
          element.style.fill = color;
          element.style.cursor = 'pointer';
          element.style.transition = 'fill 0.2s';
          
          // ホバーイベント
          element.addEventListener('mouseenter', () => {
            setHoveredPrefecture(data?.name || '');
            element.style.fill = getHoverColor(data?.count || 0);
          });
          
          element.addEventListener('mouseleave', () => {
            setHoveredPrefecture(null);
            element.style.fill = color;
          });
          
          // クリックイベント
          element.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            onPrefectureClick({
              id: prefCode,
              name: data?.name || `都道府県コード${prefCode}`
            });
          });
        }
      });
    }
  }, [svgContent, prefectureData, onPrefectureClick]);

  // SVGが読み込まれていない場合
  if (!svgContent) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <p className="text-gray-500">地図を読み込み中...</p>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* SVGコンテナ */}
      <div id="japan-map-container" style={{ flex: 1, width: '100%', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}></div>

      {/* 凡例（動的） */}
      <div className="mt-2 flex items-center justify-center gap-4 text-sm">
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-red-600"></div>
          <span>物件多({q3}+件)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-amber-500"></div>
          <span>物件中({median}+件)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-green-500"></div>
          <span>物件少(1+件)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-gray-200 border border-gray-400"></div>
          <span>データなし</span>
        </div>
      </div>

      {/* ホバー表示 */}
      {hoveredPrefecture && (
        <div className="mt-2 text-center">
          <p className="text-sm text-gray-700">{hoveredPrefecture}</p>
        </div>
      )}
    </div>
  );
}
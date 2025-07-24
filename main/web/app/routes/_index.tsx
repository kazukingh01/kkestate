import type { LoaderFunctionArgs, MetaFunction } from "react-router";
import { useLoaderData } from "react-router";
import JapanMapGeolonia from "~/components/JapanMapGeolonia";
import { getPrefectureStats } from "~/services/estate.server";

export const meta: MetaFunction = () => {
  return [
    { title: "KK Estate - 不動産データ検索・分析" },
    { name: "description", content: "日本全国の不動産データの検索・分析システム" },
  ];
};

export async function loader({}: LoaderFunctionArgs) {
  console.log("[_index.tsx] loader called");
  
  try {
    const prefectureStats = await getPrefectureStats();
    
    return Response.json({
      prefectureStats,
      timestamp: new Date().toISOString(),
      usingMockData: process.env.USE_MOCK_DATA === 'true'
    });
  } catch (error) {
    console.error('Failed to load prefecture stats:', error);
    // エラーをそのまま投げる（モックデータにフォールバックしない）
    throw new Response(`データベースエラー: ${error instanceof Error ? error.message : String(error)}`, {
      status: 500,
      statusText: "Internal Server Error"
    });
  }
}

export default function Index() {
  const { prefectureStats, usingMockData } = useLoaderData<typeof loader>();

  const handlePrefectureClick = (prefecture: { id: string; name: string }) => {
    // 分析HTMLファイルを新規タブで開く
    const analysisPath = `/analysis/map_${prefecture.id}.html`;
    window.open(analysisPath, '_blank');
  };
  return (
    <div className="h-screen bg-gray-50 overflow-hidden">
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div style={{ display: 'flex', flexDirection: 'row', gap: '2rem', height: '90vh' }}>
          {/* 左側: 検索フォーム (1/4) */}
          <div style={{ width: '33%', display: 'flex', flexDirection: 'column' }}>
            <h2 className="text-lg font-semibold mb-4">物件検索</h2>
            <div className="bg-white rounded-lg shadow-md p-6 flex-1">
              <p className="text-gray-600">検索フォームを実装予定</p>
            </div>
          </div>

          {/* 右側: 地図 (3/4) */}
          <div style={{ width: '67%', display: 'flex', flexDirection: 'column' }}>
            <div className="bg-white rounded-lg shadow-md p-4 flex-1 min-h-0" style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ flex: 1, minHeight: 0, display: 'flex' }}>
                <JapanMapGeolonia 
                  onPrefectureClick={handlePrefectureClick}
                  prefectureData={prefectureStats}
                />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
import type { LoaderFunctionArgs, MetaFunction } from "react-router";
import { useLoaderData } from "react-router";
import { getPropertyDetails } from "~/services/estate.server";
import PriceHistoryChart from "~/components/PriceHistoryChart";

export const meta: MetaFunction<typeof loader> = ({ data }) => {
  if (!data) {
    return [
      { title: "物件が見つかりません - KK Estate" },
    ];
  }

  return [
    { title: `${data.property.name || '物件詳細'} - KK Estate` },
    { name: "description", content: `${data.property.prefecture}${data.property.city}の物件詳細情報` },
  ];
};

export async function loader({ params }: LoaderFunctionArgs) {
  const { id } = params;
  
  if (!id) {
    throw new Response("物件IDが指定されていません", { status: 400 });
  }

  try {
    const propertyDetails = await getPropertyDetails(parseInt(id));
    
    if (!propertyDetails) {
      throw new Response("物件が見つかりません", { status: 404 });
    }

    return Response.json(propertyDetails);
  } catch (error) {
    console.error('Failed to load property details:', error);
    throw new Response(`データ取得エラー: ${error instanceof Error ? error.message : String(error)}`, {
      status: 500,
      statusText: "Internal Server Error"
    });
  }
}

export default function PropertyDetail() {
  const { property, priceHistory, latestDetails } = useLoaderData<typeof loader>();

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px 16px' }}>
        {/* ヘッダー */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '12px', 
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', 
          padding: '32px',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '24px' }}>
            <div style={{ flex: 1 }}>
              <h1 style={{ 
                fontSize: '28px', 
                fontWeight: 'bold', 
                color: '#111827', 
                marginBottom: '16px',
                lineHeight: '1.4'
              }}>
                {property.name || '物件名不明'}
              </h1>
              
              <div style={{ 
                display: 'inline-block',
                backgroundColor: '#f3f4f6',
                padding: '8px 16px',
                borderRadius: '20px',
                color: '#374151',
                fontSize: '16px',
                marginBottom: '24px'
              }}>
                📍 {property.prefecture} {property.city}
              </div>

              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                gap: '20px',
                fontSize: '14px'
              }}>
                <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                  <div style={{ color: '#6b7280', marginBottom: '4px' }}>物件タイプ</div>
                  <div style={{ fontWeight: '600', color: '#111827' }}>
                    {property.property_type === 'ms_new' && '🏢 新築マンション'}
                    {property.property_type === 'ms_used' && '🏢 中古マンション'}
                    {property.property_type === 'house_new' && '🏠 新築戸建て'}
                    {property.property_type === 'house_used' && '🏠 中古戸建て'}
                    {property.property_type === 'land' && '🏞️ 土地'}
                    {!['ms_new', 'ms_used', 'house_new', 'house_used', 'land'].includes(property.property_type || '') && property.property_type}
                  </div>
                </div>
                
                <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                  <div style={{ color: '#6b7280', marginBottom: '4px' }}>最終更新</div>
                  <div style={{ fontWeight: '600', color: '#111827' }}>
                    📅 {new Date(property.sys_updated).toLocaleDateString('ja-JP')}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Suumoリンク */}
            <div>
              <a
                href={`https://suumo.jp/${property.url}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-block',
                  padding: '12px 24px',
                  backgroundColor: '#10b981',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '8px',
                  fontWeight: '600',
                  fontSize: '14px',
                  transition: 'background-color 0.2s',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
                }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#059669'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#10b981'}
              >
                SUUMOで詳細を見る
              </a>
            </div>
          </div>
        </div>

        {/* 価格履歴グラフ */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '12px', 
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', 
          padding: '32px'
        }}>
          <h2 style={{ 
            fontSize: '24px', 
            fontWeight: '600', 
            marginBottom: '24px',
            color: '#111827',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            📈 価格推移
          </h2>
          {priceHistory && priceHistory.length > 0 ? (
            <PriceHistoryChart data={priceHistory} />
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '80px 20px', 
              color: '#6b7280',
              fontSize: '16px'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
              <p>価格履歴データがありません</p>
            </div>
          )}
        </div>

        {/* 最新の詳細情報 */}
        {latestDetails && latestDetails.length > 0 && (
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '12px', 
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', 
            padding: '32px',
            marginTop: '32px'
          }}>
            <h2 style={{ 
              fontSize: '24px', 
              fontWeight: '600', 
              marginBottom: '24px',
              color: '#111827',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              📋 物件詳細情報
            </h2>
            
            <div style={{ 
              overflowX: 'auto', 
              borderRadius: '8px', 
              border: '1px solid #e5e7eb' 
            }}>
              <table style={{ 
                width: '100%', 
                borderCollapse: 'collapse',
                fontSize: '14px'
              }}>
                <thead>
                  <tr style={{ backgroundColor: '#f9fafb' }}>
                    <th style={{ 
                      padding: '12px 16px', 
                      textAlign: 'left', 
                      fontWeight: '600', 
                      color: '#374151',
                      borderBottom: '1px solid #e5e7eb',
                      width: '200px'
                    }}>
                      項目
                    </th>
                    <th style={{ 
                      padding: '12px 16px', 
                      textAlign: 'left', 
                      fontWeight: '600', 
                      color: '#374151',
                      borderBottom: '1px solid #e5e7eb'
                    }}>
                      内容
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {latestDetails.map((detail, index) => (
                    <tr key={index} style={{ 
                      borderBottom: index < latestDetails.length - 1 ? '1px solid #f3f4f6' : 'none',
                      backgroundColor: index % 2 === 0 ? '#ffffff' : '#fafafa'
                    }}>
                      <td style={{ 
                        padding: '12px 16px', 
                        fontWeight: '500',
                        color: '#6b7280',
                        verticalAlign: 'top'
                      }}>
                        {detail.key}
                      </td>
                      <td style={{ 
                        padding: '12px 16px', 
                        color: '#111827',
                        verticalAlign: 'top',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word'
                      }}>
                        {detail.value}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 戻るボタン */}
        <div style={{ marginTop: '32px', textAlign: 'center' }}>
          <button
            onClick={() => window.history.back()}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              border: '2px solid #d1d5db',
              fontSize: '14px',
              fontWeight: '600',
              borderRadius: '8px',
              color: '#374151',
              backgroundColor: 'white',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#f9fafb';
              e.currentTarget.style.borderColor = '#9ca3af';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
              e.currentTarget.style.borderColor = '#d1d5db';
            }}
          >
            ← 戻る
          </button>
        </div>
      </div>
    </div>
  );
}
export default function Loading() {
  return (
    <div className="hist-page">
      <div className="hist-header">
        <h1 className="hist-title">Historical Air Quality Trends</h1>
      </div>
      <div className="hist-loading">
        <div className="hist-spinner" />
        <p>Loading historical data...</p>
      </div>
    </div>
  );
}

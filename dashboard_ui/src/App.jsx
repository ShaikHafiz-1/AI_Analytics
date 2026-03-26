import React, { useState, useEffect } from "react";
import { fetchDashboard } from "./api/client";
import samplePayload from "./mock/sample_payload.json";

import PlanningHealthCard from "./components/PlanningHealthCard";
import ForecastCard from "./components/ForecastCard";
import TrendCard from "./components/TrendCard";
import SummaryTiles from "./components/SummaryTiles";
import DatacenterCard from "./components/DatacenterCard";
import MaterialGroupCard from "./components/MaterialGroupCard";
import SupplierCard from "./components/SupplierCard";
import DesignCard from "./components/DesignCard";
import RojCard from "./components/RojCard";
import RiskCard from "./components/RiskCard";
import AIInsightCard from "./components/AIInsightCard";
import RootCauseCard from "./components/RootCauseCard";
import ActionsPanel from "./components/ActionsPanel";

const USE_MOCK = process.env.REACT_APP_USE_MOCK === "true" || !process.env.REACT_APP_API_URL;

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (USE_MOCK) {
      // Use sample payload for local dev / demo
      setTimeout(() => { setData(samplePayload); setLoading(false); }, 600);
      return;
    }
    fetchDashboard({ query_type: "summary" })
      .then(d => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState />;

  return (
    <div className="min-h-screen bg-bg text-white">
      {/* Header */}
      <header className="border-b border-border px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-white">Planning Intelligence</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            {data.filters?.locationId ? `Location: ${data.filters.locationId}` : "All Locations"}
            {data.filters?.materialGroup ? ` · Group: ${data.filters.materialGroup}` : ""}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${
            data.planningHealth?.status === "Healthy" ? "bg-green-900/30 text-accent-green" :
            data.planningHealth?.status === "Moderate" ? "bg-yellow-900/30 text-accent-yellow" :
            "bg-red-900/30 text-accent-red"
          }`}>
            {data.planningHealth?.status}
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 flex flex-col gap-6">

        {/* Row 1: Health + Forecast + Trend */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <PlanningHealthCard score={data.planningHealth?.score} status={data.planningHealth?.status} />
          <ForecastCard
            forecastNew={data.forecastNew}
            forecastOld={data.forecastOld}
            trendDelta={data.trendDelta}
            trendDirection={data.trendDirection}
          />
          <TrendCard
            trendDirection={data.trendDirection}
            changeDrivers={data.changeDrivers}
            totalRecords={data.totalRecords}
            changedRecordCount={data.changedRecordCount}
          />
        </div>

        {/* Row 2: KPI tiles */}
        <SummaryTiles data={data} />

        {/* Row 3: AI Insight (full width) */}
        <AIInsightCard aiInsight={data.aiInsight} />

        {/* Row 4: Datacenter + Material Groups */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <DatacenterCard datacenterSummary={data.datacenterSummary} />
          <MaterialGroupCard materialGroupSummary={data.materialGroupSummary} />
        </div>

        {/* Row 5: Supplier + Design + ROJ */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SupplierCard supplierSummary={data.supplierSummary} />
          <DesignCard designSummary={data.designSummary} />
          <RojCard rojSummary={data.rojSummary} />
        </div>

        {/* Row 6: Risk + Root Cause */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <RiskCard riskSummary={data.riskSummary} />
          <RootCauseCard rootCause={data.rootCause} />
        </div>

        {/* Row 7: Actions */}
        <ActionsPanel
          recommendedActions={data.recommendedActions}
          onAskCopilot={() => alert("Opening Copilot Studio...")}
          onNotifyPlanner={() => alert("Notifying planner...")}
          onViewDetails={() => alert("Opening detail view...")}
        />

      </main>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-bg flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-accent-blue border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-400 text-sm">Loading planning data...</p>
      </div>
    </div>
  );
}

function ErrorState({ message }) {
  return (
    <div className="min-h-screen bg-bg flex items-center justify-center">
      <div className="bg-card border border-accent-red/30 rounded-2xl p-8 max-w-md text-center">
        <p className="text-accent-red text-lg font-semibold mb-2">Failed to load dashboard</p>
        <p className="text-gray-400 text-sm">{message}</p>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="min-h-screen bg-bg flex items-center justify-center">
      <div className="bg-card border border-border rounded-2xl p-8 max-w-md text-center">
        <p className="text-gray-300 text-lg font-semibold mb-2">No planning data available</p>
        <p className="text-gray-500 text-sm">Send current and previous rows to the backend to see insights.</p>
      </div>
    </div>
  );
}

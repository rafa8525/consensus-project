import React, { useEffect, useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function Dashboard() {
  const [bmiData, setBmiData] = useState([]);
  const [mealData, setMealData] = useState([]);

  useEffect(() => {
    fetch("/data/weekly_nutrition_summary.json")
      .then(res => res.json())
      .then(data => {
        setMealData(data);
        const bmiSample = [
          { date: "2025-06-10", bmi: 24.6 },
          { date: "2025-06-11", bmi: 24.7 },
          { date: "2025-06-12", bmi: 24.8 },
          { date: "2025-06-13", bmi: 24.8 }
        ];
        setBmiData(bmiSample);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-6 grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      {/* BMI Trend Line Chart */}
      <div className="rounded-2xl shadow p-4 bg-white col-span-full">
        <h2 className="text-xl font-bold mb-2">BMI Trend</h2>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={bmiData}>
            <XAxis dataKey="date" />
            <YAxis domain={[24.0, 25.5]} />
            <Tooltip />
            <Line type="monotone" dataKey="bmi" stroke="#8884d8" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Meal Frequency Bar Chart */}
      <div className="rounded-2xl shadow p-4 bg-white col-span-full">
        <h2 className="text-xl font-bold mb-2">Meal Frequency</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={mealData}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Bar dataKey={() => 1} fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

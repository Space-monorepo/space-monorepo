import { motion } from "framer-motion";

const reputationLevels = ["Sub-observação", "Ajudante", "Colaborador", "Líder"];

const getReputationPercentage = (level?: string) => {
  const index = reputationLevels.indexOf(level || "Sub-observação");
  const percentage = ((index + 0.5) / reputationLevels.length) * 100;
  return `${percentage}%`;
};

export default function ReputationBar({ reputationLevel }: { reputationLevel?: string }) {
  const level = reputationLevel || "Sub-observação";
  const percentage = getReputationPercentage(level);

  return (
    <div className="mt-4 border-t pt-4">
      <div className="flex justify-between text-sm mb-2">
        <h3 className="font-medium">Reputação</h3>
        <span className="text-gray-500">{level}</span>
      </div>

      <div className="relative h-2 w-full bg-gray-200 rounded-full overflow-hidden">
        <div className="absolute h-full top-0 left-0 right-0 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500" />

        <motion.div
          className="absolute -top-4"
          initial={{ left: "0%" }}
          animate={{ left: percentage }}
          transition={{ type: "spring", stiffness: 80, damping: 12 }}
          style={{ transform: "translateX(-50%)" }}
        >
          <div className="w-0 h-0 border-l-4 border-r-4 border-b-8 border-l-transparent border-r-transparent border-b-black mx-auto" />
        </motion.div>
      </div>

      <div className="flex justify-between text-xs text-gray-500 mt-3">
        {reputationLevels.map((level) => (
          <span key={level} className="w-1/4 text-center">{level}</span>
        ))}
      </div>
    </div>
  );
}

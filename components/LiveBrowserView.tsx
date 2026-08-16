import { motion } from 'framer-motion';

export default function LiveBrowserView({
  url,
  state
}: {
  url: string;
  state: string;
}) {
  const isIntervention = state === 'intervention';

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="relative w-full h-full"
    >

      {/* The actual interactive live browser */}

      <iframe
        src={url}
        className="w-full h-full bg-black"
        allow="clipboard-read; clipboard-write"
      />

      {/* Overlay for Agent Status / Human Intervention Prompt */}

      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className={`absolute top-4 left-1/2 -translate-x-1/2 px-6 py-3 rounded-full border backdrop-blur-xl shadow-lg transition-all duration-500 ${
          isIntervention
            ? 'bg-amber-500/20 border-amber-400/50 text-amber-100'
            : 'bg-white/5 border-white/10 text-gray-200'
        }`}
      >

        <div className="flex items-center gap-2 text-sm font-medium">

          {isIntervention ? (
            <>
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3.334 1.732 3.334z"
                />
              </svg>

              Human Intervention Required
            </>
          ) : (
            <>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />

              Agent Active
            </>
          )}

        </div>

      </motion.div>

    </motion.div>
  );
}
